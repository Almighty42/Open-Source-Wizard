# Deploying Open Source Wizard (opensourcewizard.com)

Runbook for running the site on a DigitalOcean droplet behind Cloudflare, updating it with `deploy/deploy.sh`, and rebuilding it from scratch.
Contains no secrets. Never commit `.env`, `origin.key`, `origin.pem`, database files or passwords.

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
| Backups on server | `/srv/osw/backups/` |
| Service | `osw` (`deploy/osw.service`) |
| nginx site | `deploy/osw.nginx.conf` |
| Update script | `deploy/deploy.sh` (run from your laptop) |
| Server Python | 3.12 (Ubuntu 24.04); local development uses 3.14. The app was verified to import and run on 3.12. |

Files in `deploy/`:

| File | Purpose |
|---|---|
| `DEPLOY.md` | This runbook |
| `deploy.sh` | One-command update from your laptop (section 11) |
| `osw.service` | systemd unit for Gunicorn |
| `osw.nginx.conf` | nginx site config |

## 0. Before you start (rebuilding from scratch)

- [ ] The repo contains `migrations/`, `gunicorn` in `requirements.txt`, and `deploy/`.
- [ ] `config.py` refuses to start in production without `SECRET_KEY`.
- [ ] `ProxyFix` is enabled in `create_app` (needed so rate limiting and logs see real visitor IPs).
- [ ] Cloudflare zone for `opensourcewizard.com` is Active (`dig NS opensourcewizard.com +short` shows two `*.ns.cloudflare.com`).
- [ ] SSH key available: `~/.ssh/digitalocean-ssh-key` (and `.pub` uploaded to DigitalOcean > Settings > Security).
- [ ] Generated a new SECRET_KEY and saved it in your password manager:
  `python3 -c "import secrets; print(secrets.token_hex(32))"`

## 1. Create the droplet

- Image: Ubuntu LTS. Plan: Basic shared CPU. 1 GiB RAM is comfortable; 512 MiB works only with swap (section 3).
- Authentication: SSH key only. Region: closest to you (for example Frankfurt).
- IPv6: not needed (Cloudflare serves IPv6 visitors and talks to the origin over IPv4).
- Optional: enable DigitalOcean weekly backups (20% of the droplet price). Set a billing alert.
- Note the public IPv4 address, referred to below as `SERVER_IP`.
- Resizing later: power off, Resize, choose "CPU and RAM only" (reversible). Choosing disk as well is permanent.

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

Shortcut in `~/.ssh/config` on your laptop (the deploy script uses the `osw` alias):

```
Host osw
    HostName SERVER_IP
    User deploy
    IdentityFile ~/.ssh/digitalocean-ssh-key
```

The key has a passphrase, so load it once per session: `ssh-add ~/.ssh/digitalocean-ssh-key`.

If the droplet is ever recreated, the IP changes: update `HostName` here and both A records in Cloudflare. SSH will warn about a changed host key; remove the old entry with `ssh-keygen -R SERVER_IP` (only when you know the server was rebuilt).

## 3. Install packages

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-venv python3-pip nginx git sqlite3 unattended-upgrades
python3 --version
```

Local development uses Python 3.14 and the server uses Ubuntu's 3.12. This works today, but test on the server's Python (`pip install` plus starting the app) after large dependency upgrades. Do not run `do-release-upgrade` on a 512 MiB droplet.

Optional swap for the 512 MiB plan:

```bash
sudo fallocate -l 1G /swapfile && sudo chmod 600 /swapfile
sudo mkswap /swapfile && sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

With 512 MiB, watch `free -h` after startup. If memory is tight, change `--workers 2` to `--workers 1` in `/etc/systemd/system/osw.service`, then `sudo systemctl daemon-reload && sudo systemctl restart osw`.

## 4. Get the code

```bash
sudo mkdir -p /srv/osw && sudo chown deploy:deploy /srv/osw
git clone https://github.com/Almighty42/Open-Source-Wizard.git /srv/osw
cd /srv/osw
python3 -m venv venv
./venv/bin/pip install --no-cache-dir -r requirements.txt
mkdir -p logs backups
```

Verify the app imports (any throwaway key works here):

```bash
SECRET_KEY=test ./venv/bin/python -c "from run import app; print('ok')"
```

Check `git ls-files app/static/uploads`. If it lists the Faker demo uploads, remove them from git so dummy content does not ship to production. Also confirm `app/static/css/app.css` exists (compiled Sass); if not, build it first.

The server clones over HTTPS without credentials, so the repository must stay public. If it ever becomes private, add a read-only deploy key on the server instead of putting tokens in the URL or in scripts.

## 5. Create `.env`

Generate the file with a fresh key in one step:

```bash
cd /srv/osw
cat > .env <<EOF
SECRET_KEY=$(./venv/bin/python -c "import secrets; print(secrets.token_hex(32))")
DEBUG=False
ADMIN_USERNAME=YOUR_ADMIN_USERNAME
LOG_LEVEL=INFO
LOG_DIR=/srv/osw/logs
HOST=127.0.0.1
PORT=3001
EOF
chmod 600 .env
grep SECRET_KEY .env      # copy the value into your password manager
```

Optional: `SITE_URL=https://opensourcewizard.com` (used by the sitemap and robots.txt; this is already the default).

Do not set `DATABASE_URL`; the default is `/srv/osw/app.db`. Keep the same `SECRET_KEY` permanently, otherwise all sessions are invalidated. All Gunicorn workers must share the key, which they do because it comes from `.env`.

## 6. Create the database and admin user

The local `app.db` contains Faker demo data. Do NOT copy it to the server and do NOT run any `flask seed ...` command in production.

```bash
cd /srv/osw
export FLASK_APP=run.py
./venv/bin/flask db upgrade
sqlite3 app.db ".tables"
./venv/bin/flask shell
```

`flask db upgrade` applies the migrations in `migrations/` (currently one revision, `initial_schema`). In the shell (`db` is provided by the app's shell context):

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

Expect `HTTP/1.1 200 OK`. If not, read `journalctl -u osw -n 50 --no-pager`.

Allow the deploy user to restart the service without a password. This is required by `deploy/deploy.sh`. The rule allows exactly one command and nothing else:

```bash
echo 'deploy ALL=(root) NOPASSWD: /usr/bin/systemctl restart osw' | sudo tee /etc/sudoers.d/osw-deploy
sudo chmod 440 /etc/sudoers.d/osw-deploy
sudo visudo -cf /etc/sudoers.d/osw-deploy
```

The last command must report that the file parsed OK. Test with `sudo -n systemctl restart osw` (it must not ask for a password).

## 8. nginx with a Cloudflare Origin certificate

1. Cloudflare dashboard > SSL/TLS > Origin Server > Create Certificate. Hostnames: `opensourcewizard.com` and `*.opensourcewizard.com`. The private key is shown only once.
2. Save the certificate and private key on the server:

```bash
sudo mkdir -p /etc/ssl/osw
sudo nano /etc/ssl/osw/origin.pem
sudo nano /etc/ssl/osw/origin.key
sudo chmod 600 /etc/ssl/osw/origin.key
sudo chmod 644 /etc/ssl/osw/origin.pem
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

nginx serves only `/static/` directly from `/srv/osw/app/static/`. Everything else, including `/robots.txt` and `/sitemap.xml`, goes to Gunicorn. The database, `.env` and `backups/` are outside the static directory and are not reachable over HTTP.

## 9. Cloudflare and DNS

1. DNS: A record `@` -> `SERVER_IP`, and A (or CNAME) `www`. Proxy status: Proxied (orange cloud). Edit the existing records instead of adding duplicates. There should be no AAAA record.
2. Leave the five `eforward*.registrar-servers.com` MX records and the SPF TXT record alone: they belong to Namecheap email forwarding, not to the website. Keep them DNS only.
3. SSL/TLS > Overview: set encryption mode to **Full (strict)**.
4. SSL/TLS > Edge Certificates: enable **Always Use HTTPS**.
5. Test from your laptop:

```bash
dig A opensourcewizard.com +short
curl -sI --max-time 30 https://opensourcewizard.com | grep -iE "^(HTTP|server|cf-ray)"
```

Expect `HTTP/2 200` and `server: cloudflare`.

6. Lock the origin to Cloudflare only (so nobody can bypass it or spoof `CF-Connecting-IP`). Do this only after the site works through Cloudflare. SSH is unaffected.

```bash
for ip in $( (curl -s https://www.cloudflare.com/ips-v4; echo; curl -s https://www.cloudflare.com/ips-v6) ); do
  sudo ufw allow from "$ip" to any port 443 proto tcp
done
sudo ufw status numbered
sudo ufw delete allow 443/tcp
sudo ufw delete allow 80/tcp
sudo ufw status numbered
```

Verify: the public site still returns 200, and `curl -sk --max-time 5 https://SERVER_IP` times out. Cloudflare's IP ranges change rarely; re-run the loop occasionally and check [https://www.cloudflare.com/ips/](https://www.cloudflare.com/ips/).

## 10. Verification checklist

- [ ] Homepage, articles, projects, about, and a 404 page load over HTTPS.
- [ ] Admin login works; session cookie shows `Secure` and `HttpOnly` in browser dev tools.
- [ ] Create and publish the real post; upload an image and confirm it loads from `/static/uploads/...`.
- [ ] Hammer the login form until the limiter returns 429, then confirm other visitors (for example your phone on mobile data) are not blocked, and that `/srv/osw/logs/app.log` shows real client IPs, not `127.0.0.1`.
- [ ] `sudo reboot`, then confirm the site returns by itself (systemd and nginx both enabled).

## 11. Updating the site (`deploy/deploy.sh`)

Normal workflow: commit on `main` on your laptop, then run the script from the repository.

```bash
deploy/deploy.sh            # deploy what is already pushed
deploy/deploy.sh --push     # push local commits first, then deploy
deploy/deploy.sh --force    # restart even if the server is already up to date
```

One-time prerequisites:
- The `osw` host alias in `~/.ssh/config` (section 2) and `ssh-add ~/.ssh/digitalocean-ssh-key` once per session.
- The passwordless restart rule in `/etc/sudoers.d/osw-deploy` (section 7).
- The script is executable: `chmod +x deploy/deploy.sh`.

What the script does:
1. Local checks: you are on `main`, tracked files are committed, and local commits are pushed (or pushes them with `--push`).
2. On the server: `git fetch`, then a fast-forward-only merge into `/srv/osw`.
3. Runs `pip install` only if `requirements.txt` changed.
4. If anything under `migrations/` changed: backs up `app.db` to `/srv/osw/backups/pre-deploy-<timestamp>.db`, then runs `flask db upgrade`.
5. Restarts the `osw` service and polls `http://127.0.0.1:3001/` for up to 20 seconds.
6. Checks that `https://opensourcewizard.com` returns 200 through Cloudflare.
7. Prints a reminder if `deploy/osw.nginx.conf` or `deploy/osw.service` changed, because those need manual installation (below).

Rollback behaviour: if any server step fails or the health check times out, the script resets the code to the previous commit and restarts the service. It does not undo database migrations. If a migration ran, restore the printed `pre-deploy-*.db` backup (stop the service, copy the file over `/srv/osw/app.db`, start the service).

Options via environment variables: `OSW_HOST` (default `osw`), `OSW_BRANCH` (`main`), `OSW_APP_DIR` (`/srv/osw`), `OSW_SERVICE` (`osw`), `OSW_PORT` (`3001`), `OSW_SITE_URL` (`https://opensourcewizard.com`).

Things the script does not do:
- It does not install nginx or systemd file changes. When `deploy/osw.nginx.conf` changes: `sudo cp /srv/osw/deploy/osw.nginx.conf /etc/nginx/sites-available/osw && sudo nginx -t && sudo systemctl reload nginx`. When `deploy/osw.service` changes: `sudo cp /srv/osw/deploy/osw.service /etc/systemd/system/osw.service && sudo systemctl daemon-reload && sudo systemctl restart osw`.
- It discards manual edits on the server (`git reset --hard` on rollback, fast-forward-only merge otherwise). Never edit files directly on the droplet.
- It does not change `.env`. Edit that on the server and restart with `sudo systemctl restart osw`.
- It does not rebuild Sass. Commit the compiled `app/static/css/app.css`.

Manual fallback (what the script automates):

```bash
ssh osw
cd /srv/osw
git pull --ff-only
./venv/bin/pip install --no-cache-dir -r requirements.txt
FLASK_APP=run.py ./venv/bin/flask db upgrade
sudo systemctl restart osw
```

## 12. Backups (do not skip)

The database and uploads exist only on the server. Nightly database backup via cron (`crontab -e` as `deploy`; `%` must be escaped). The second command prunes both nightly and pre-deploy backups so the disk does not fill up and old database copies do not pile up:

```
0 3 * * * sqlite3 /srv/osw/app.db ".backup '/srv/osw/backups/app-$(date +\%F).db'"
30 3 * * * find /srv/osw/backups \( -name 'app-*.db' -o -name 'pre-deploy-*.db' \) -mtime +14 -delete
```

Backups contain password hashes. Keep `/srv/osw/backups` mode 700 (`chmod 700 /srv/osw/backups`) and never copy them anywhere public.

Pull copies to your laptop (run from the laptop, weekly or from a cron job):

```bash
mkdir -p ~/osw-backups
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
| `deploy.sh`: `Permission denied (publickey)` | SSH key not loaded | `ssh-add ~/.ssh/digitalocean-ssh-key`; check the `osw` alias |
| `deploy.sh`: `sudo: a password is required` | Sudoers rule missing or wrong path | Section 7; `command -v systemctl` should be `/usr/bin/systemctl` |
| `deploy.sh`: `local commit(s) not pushed` | Unpushed commits | `git push` or run with `--push` |
| `deploy.sh`: health check failed, rolled back | New code crashes on start | `ssh osw 'journalctl -u osw -n 100 --no-pager'`, fix, redeploy |
| `deploy.sh`: public site not 200 | Cloudflare or origin problem | Rows above; the app itself passed its local health check |
| Sitemap or robots.txt returns 404 | Routes not deployed | Confirm the code is on the server and the service restarted |

Logs: `/srv/osw/logs/app.log`, `/srv/osw/logs/error.log`, `journalctl -u osw`, `/var/log/nginx/error.log`.

## 15. Recurring reminders

- Namecheap domain renewal: May 2027.
- DigitalOcean payment method valid and billing alert set (a lapsed payment is what took the site down before).
- Monthly: `sudo apt update && sudo apt upgrade`, verify a recent backup exists, and pull a copy to your laptop.
- Occasionally: re-run the Cloudflare IP firewall loop (section 9.6).

## 16. SEO: robots.txt, sitemap and Google Search Console

The app serves both files itself: `/robots.txt` and `/sitemap.xml` (routes in `app/blueprints/main/routes.py`, canonical host from `SITE_URL`). The sitemap is generated from the database on each request, so newly published articles and projects appear automatically. Drafts are excluded.

Verify after each deploy that touches them:

```bash
curl -s https://opensourcewizard.com/robots.txt
curl -s https://opensourcewizard.com/sitemap.xml | head -n 20
```

Search Console setup (after a rebuild, or if the property shows as unverified):
1. Add a **Domain** property for `opensourcewizard.com`.
2. Add the TXT record it shows in Cloudflare DNS (type TXT, name `@`, DNS only). Keep the existing SPF TXT record.
3. Click Verify (wait a few minutes if it fails).
4. Sitemaps > submit `sitemap.xml`.
5. URL Inspection > run a live test and Request Indexing for the homepage and key posts.

After downtime, recovery is automatic once pages return 200, but the crawl rate ramps up gradually. Keep the slugs of existing posts unchanged, and keep the site stable. Googlebot gets slowed by 5xx and 429 responses, so watch Crawl Stats and `sudo grep " 429 " /var/log/nginx/access.log`. The rate limiter's defaults (3/second, 75/hour, 200/day per IP) apply to every route; exempt `sitemap()` and `robots()` with `@limiter.exempt`.
