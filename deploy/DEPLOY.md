# Deploying Open Source Wizard (opensourcewizard.com)

Runbook for rebuilding the site on a fresh DigitalOcean droplet behind Cloudflare.
Contains no secrets. Never commit `.env`, `origin.key`, `origin.pem` or passwords.

## Architecture

```
Browser -> Cloudflare (proxy, public HTTPS)
        -> nginx :443 (Cloudflare Origin certificate)
        -> Gunicorn 127.0.0.1:3001 (systemd service "osw")
        -> Flask app (run:app) -> SQLite (/srv/osw/app.db)
```

| Item | Value |
|---|---|
| Server user | `deploy` |
| App directory | `/srv/osw` |
| Virtualenv | `/srv/osw/venv` |
| Database | `/srv/osw/app.db` (SQLite) |
| Uploads | `/srv/osw/app/static/uploads/` (exists only on the server, back it up) |
| Service | `osw` (`deploy/osw.service`) |
| nginx site | `deploy/osw.nginx.conf` |

## 0. Before you start (on your laptop)

- [ ] The repo contains `migrations/`, `gunicorn` in `requirements.txt`, and `deploy/`.
- [ ] `config.py` refuses to start in production without `SECRET_KEY`.
- [ ] `ProxyFix` is enabled in `create_app` (needed so rate limiting sees real visitor IPs).
- [ ] Cloudflare zone for `opensourcewizard.com` is Active (`dig NS opensourcewizard.com +short` shows two `*.ns.cloudflare.com`).
- [ ] SSH key available: `~/.ssh/digitalocean-ssh-key` (and `.pub` uploaded to DigitalOcean > Settings > Security).
- [ ] Generated a new SECRET_KEY and saved it in your password manager:
  `python3 -c "import secrets; print(secrets.token_hex(32))"`

## 1. Create the droplet

- Image: Ubuntu LTS. Plan: Basic shared CPU, 1 GiB RAM (512 MiB works only with swap).
- Authentication: SSH key only. Region: closest to you (for example Frankfurt).
- Optional: enable DigitalOcean backups. Set a billing alert.
- Note the public IPv4 address, referred to below as `SERVER_IP`.

## 2. First login and hardening

```bash
ssh -i ~/.ssh/digitalocean-ssh-key root@SERVER_IP
adduser deploy
usermod -aG sudo deploy
rsync --archive --chown=deploy:deploy ~/.ssh /home/deploy
```

Open a second terminal and confirm `ssh -i ~/.ssh/digitalocean-ssh-key deploy@SERVER_IP` works and `sudo -v` works. Only then disable root and password login. The file name starts with `00` because sshd uses the first value it reads, and cloud images ship `50-cloud-init.conf`.

```bash
sudo tee /etc/ssh/sshd_config.d/00-hardening.conf <<'EOF'
PermitRootLogin no
PasswordAuthentication no
EOF
sudo sshd -T | grep -E "permitrootlogin|passwordauthentication"
sudo systemctl restart ssh
```

Firewall (tightened further in section 9):

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

Optional shortcut in `~/.ssh/config` on your laptop:

```
Host osw
    HostName SERVER_IP
    User deploy
    IdentityFile ~/.ssh/digitalocean-ssh-key
```

## 3. Install packages

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-venv python3-pip nginx git sqlite3 unattended-upgrades
python3 --version
```

Your local development uses Python 3.14. If the server's Python differs, run the app once and check for errors in `pip install` or at startup before continuing.

Optional swap for the 512 MiB plan:

```bash
sudo fallocate -l 1G /swapfile && sudo chmod 600 /swapfile
sudo mkswap /swapfile && sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## 4. Get the code

```bash
sudo mkdir -p /srv/osw && sudo chown deploy:deploy /srv/osw
git clone https://github.com/Almighty42/Open-Source-Wizard.git /srv/osw
cd /srv/osw
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
mkdir -p logs backups
```

Check `git ls-files app/static/uploads`. If it lists the Faker demo uploads, remove them from git so dummy content does not ship to production. Also confirm `app/static/css/app.css` exists (compiled Sass); if not, build it first.

## 5. Create `.env`

```bash
nano /srv/osw/.env
chmod 600 /srv/osw/.env
```

Template:

```
SECRET_KEY=PASTE_THE_GENERATED_KEY
DEBUG=False
ADMIN_USERNAME=YOUR_ADMIN_USERNAME
LOG_LEVEL=INFO
LOG_DIR=/srv/osw/logs
HOST=127.0.0.1
PORT=3001
```

Do not set `DATABASE_URL`; the default is `/srv/osw/app.db`. Keep the same `SECRET_KEY` forever, otherwise all sessions are invalidated. All Gunicorn workers must read the same key, which they do because it comes from `.env`.

## 6. Create the database and admin user

The local `app.db` contains Faker demo data. Do NOT copy it to the server and do NOT run any `flask seed ...` command in production.

```bash
cd /srv/osw
export FLASK_APP=run.py
./venv/bin/flask db upgrade
./venv/bin/flask shell
```

In the shell (`db` is provided by the app's shell context):

```python
import getpass
from app.models import User
u = User(username="YOUR_ADMIN_USERNAME", is_admin=True, login_attempts=0)
u.set_password(getpass.getpass("Password: "))
db.session.add(u)
db.session.commit()
exit()
```

The username must match `ADMIN_USERNAME` in `.env`. Passwords are stored hashed, so they can be reset but never recovered.

## 7. Gunicorn service (systemd)

```bash
sudo cp /srv/osw/deploy/osw.service /etc/systemd/system/osw.service
sudo systemctl daemon-reload
sudo systemctl enable --now osw
sudo systemctl status osw --no-pager
curl -I http://127.0.0.1:3001
```

Expect an HTTP response from Flask. If not, read `journalctl -u osw -n 50 --no-pager`.

## 8. nginx with a Cloudflare Origin certificate

1. Cloudflare dashboard > SSL/TLS > Origin Server > Create Certificate. Hostnames: `opensourcewizard.com` and `*.opensourcewizard.com`.
2. Save the certificate and private key on the server:

```bash
sudo mkdir -p /etc/ssl/osw
sudo nano /etc/ssl/osw/origin.pem
sudo nano /etc/ssl/osw/origin.key
sudo chmod 600 /etc/ssl/osw/origin.key
```

3. Enable the site:

```bash
sudo cp /srv/osw/deploy/osw.nginx.conf /etc/nginx/sites-available/osw
sudo ln -s /etc/nginx/sites-available/osw /etc/nginx/sites-enabled/osw
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
```

4. Test locally (`-k` is needed because the Origin CA is only trusted by Cloudflare):

```bash
curl -skI --resolve opensourcewizard.com:443:127.0.0.1 https://opensourcewizard.com
```

## 9. Cloudflare and DNS

1. DNS: A record `@` -> `SERVER_IP`, and A or CNAME `www`. Proxy status: Proxied (orange cloud).
2. SSL/TLS > Overview: set encryption mode to **Full (strict)**.
3. SSL/TLS > Edge Certificates: enable **Always Use HTTPS**.
4. Test from your laptop:

```bash
dig A opensourcewizard.com +short
curl -sI --max-time 30 https://opensourcewizard.com | grep -iE "^(HTTP|server|cf-ray)"
```

Expect `HTTP/2 200` and `server: cloudflare`.

5. Lock the origin to Cloudflare only (so nobody can bypass it or spoof `CF-Connecting-IP`):

```bash
for ip in $( (curl -s https://www.cloudflare.com/ips-v4; echo; curl -s https://www.cloudflare.com/ips-v6) ); do
  sudo ufw allow from "$ip" to any port 443 proto tcp
done
sudo ufw delete allow 443/tcp
sudo ufw delete allow 80/tcp
sudo ufw status numbered
```

Cloudflare's IP ranges change rarely; re-run this loop occasionally and check https://www.cloudflare.com/ips/ .

## 10. Verification checklist

- [ ] Homepage, articles, projects, about, and a 404 page load over HTTPS.
- [ ] Admin login works; session cookie shows `Secure` and `HttpOnly` in browser dev tools.
- [ ] Create and publish the real post; upload an image and confirm it loads from `/static/uploads/...`.
- [ ] Hammer the login form until the limiter returns 429, then confirm other visitors (for example your phone on mobile data) are not blocked.
- [ ] `sudo reboot`, then confirm the site returns by itself (systemd and nginx both enabled).

## 11. Updating the site

```bash
ssh osw
cd /srv/osw
git pull
./venv/bin/pip install -r requirements.txt
FLASK_APP=run.py ./venv/bin/flask db upgrade
sudo systemctl restart osw
```

If you change the nginx config: `sudo nginx -t && sudo systemctl reload nginx`.

## 12. Backups (do not skip)

The database and uploads exist only on the server. Nightly database backup via cron (`crontab -e` as `deploy`; `%` must be escaped):

```
0 3 * * * sqlite3 /srv/osw/app.db ".backup '/srv/osw/backups/app-$(date +\%F).db'" && find /srv/osw/backups -name 'app-*.db' -mtime +14 -delete
```

Pull copies to your laptop (run from the laptop, weekly or from a cron job):

```bash
rsync -avz osw:/srv/osw/backups/ ~/osw-backups/db/
rsync -avz osw:/srv/osw/app/static/uploads/ ~/osw-backups/uploads/
scp osw:/srv/osw/.env ~/osw-backups/env.backup   # store in an encrypted location
```

Restore on a new server: clone the repo, restore `.env`, run `flask db upgrade`, stop the service, copy a backup over `/srv/osw/app.db`, restore `uploads/`, then start the service.

## 13. Reset the admin password

```bash
cd /srv/osw && FLASK_APP=run.py ./venv/bin/flask shell
```

```python
import getpass
admin.set_password(getpass.getpass("New password: "))
db.session.commit()
```

`admin` is the user whose username equals `ADMIN_USERNAME` in `.env`.

## 14. Troubleshooting

| Symptom | Likely cause | Check |
|---|---|---|
| Cloudflare 521 | Origin refuses connections | `systemctl status nginx`, `ufw status`, nginx listening on 443 |
| Cloudflare 522 / curl hangs | Origin unreachable or droplet gone | Is the droplet running? Is the DNS record's IP correct? |
| Cloudflare 525 / 526 | TLS problem on origin | Origin certificate paths in nginx; certificate hostnames; SSL mode |
| 502 Bad Gateway | Gunicorn down | `journalctl -u osw -n 100 --no-pager` |
| Login does not stick | Not using HTTPS (cookies are `Secure`) | Browse via `https://`; check `X-Forwarded-Proto` |
| Everyone gets 429 | Limiter sees one proxy IP | `ProxyFix` missing or `CF-Connecting-IP` not forwarded |
| App crashes at start with SECRET_KEY error | `.env` missing key | Check `/srv/osw/.env` |
| Missing tables | Migrations not applied | `flask db upgrade`; check `migrations/` is in git |

Logs: `/srv/osw/logs/app.log`, `/srv/osw/logs/error.log`, `journalctl -u osw`, `/var/log/nginx/error.log`.

## 15. Recurring reminders

- Namecheap domain renewal: May 2027.
- DigitalOcean payment method valid and billing alert set (a lapsed payment is what took the site down before).
- Monthly: `sudo apt update && sudo apt upgrade`, verify a recent backup exists.
