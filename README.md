<div align="center">
  <img width="510" height="150" alt="Open Source Wizard logo" src="https://github.com/user-attachments/assets/aae04c99-998d-4182-8684-85c00b7b72fe" />

  **Source code for [opensourcewizard.com](https://opensourcewizard.com), a blog about embedded systems, electronics and DIY hardware.**

  ![Python](https://img.shields.io/badge/python-3.12+-blue) ![Flask](https://img.shields.io/badge/flask-3.1-black) ![License](https://img.shields.io/badge/license-MIT-green)
</div>

<img width="1337" height="695" alt="Screenshot of the homepage" src="https://github.com/user-attachments/assets/0f074916-ec17-4d85-942c-9ea86dcc3842" />

## Features

- Write articles and projects in Markdown, with syntax-highlighted code blocks and sanitized HTML output
- Tags, categories, and attached images, videos and files for every post
- Admin panel for writing, editing and publishing content
- Light and dark theme
- Rate limiting and account lockout on login

## Tech stack

- **Backend:** Python, Flask
- **Database:** SQLite
- **Frontend:** Jinja templates, Sass, JavaScript
- **Hosting:** DigitalOcean, Cloudflare

## Run locally

**Requirements:** Python 3.12 or newer and Git.

```bash
# 1. Clone the repository
git clone https://github.com/Almighty42/Open-Source-Wizard.git
cd Open-Source-Wizard

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure the environment
cp .env.example .env

# 5. Create the database
flask db upgrade

# 6. (Optional) Fill it with fake demo content
flask seed all

# 7. Start the development server
flask run --port 3001
```

Then open [http://127.0.0.1:3001](http://127.0.0.1:3001).

### Configuration

Edit `.env` before the first run:

| Variable | Description | Example |
|---|---|---|
| `DEBUG` | Use `True` locally. Without it, the app refuses to start unless `SECRET_KEY` is set | `True` |
| `SECRET_KEY` | Required in production. Generate with `python -c "import secrets; print(secrets.token_hex(32))"` | |
| `ADMIN_USERNAME` | Username of the admin account | `admin` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |
| `LOG_DIR` | Where log files are written | `logs` |
| `HOST` / `PORT` | Bind address and port | `127.0.0.1` / `3001` |
| `SITE_URL` | Canonical URL used in the sitemap | `https://opensourcewizard.com` |

### Admin account

The admin user is created through the Flask shell, so no password lives in the code:

```bash
flask shell
```

```python
import getpass
from app.models import User
u = User(username="admin", is_admin=True, login_attempts=0)
u.set_password(getpass.getpass("Password: "))
db.session.add(u)
db.session.commit()
exit()
```

The username must match `ADMIN_USERNAME` in `.env`. Then log in at `/login`.

### Note on HTTPS

Session cookies are marked `Secure`, so logging in over plain `http://` may not work in every browser. Chrome and Firefox treat `localhost` and `127.0.0.1` as secure contexts and normally accept them. If login doesn't stick, test over HTTPS.

### Styles

Styles are written in Sass under `app/static/scss/` and compiled to `app/static/css/app.css`, which is committed. To change styles, recompile:

```bash
pip install libsass            # or: npm install -g sass
sass app/static/scss/app.scss app/static/css/app.css
```

## Deployment

The site is hosted on DigitalOcean behind Cloudflare. Server setup, configuration and troubleshooting are documented in [deploy/DEPLOY.md](deploy/DEPLOY.md).

Updating the live site from your machine:

```bash
git push                    # commit your changes to main first
deploy/deploy.sh            # deploy what's already pushed
deploy/deploy.sh --push     # push local commits, then deploy
```

The script pulls the new code on the server, installs changed dependencies, backs up and migrates the database when migrations changed, restarts the service and checks that the site responds. If a step fails, it rolls the code back to the previous commit.

### Weekly report

A weekly systemd timer on the server writes a health report (traffic, 5xx/429 counts, app and nginx errors, service status, disk, backup age). The owner's laptop fetches it over a restricted SSH key and shows a desktop notification. See [deploy/DEPLOY.md](deploy/DEPLOY.md#17-weekly-report) for setup.

## Project Structure

```text
Open-Source-Wizard/
├── app/
│   ├── blueprints/       # Routes, one package per area
│   │   ├── admin/        # Content management (routes, services, selectors)
│   │   ├── api/
│   │   ├── articles/
│   │   ├── auth/         # Login, logout, lockout
│   │   ├── errors/       # 404, 429 and 500 handlers
│   │   ├── main/         # Home, about, sitemap.xml, robots.txt
│   │   └── projects/
│   ├── filters/          # Markdown rendering, code blocks, HTML sanitizing
│   ├── forms/            # WTForms definitions
│   ├── middlewares/      # Request hooks
│   ├── models/           # SQLAlchemy models
│   ├── seeders/          # Fake demo data for development
│   ├── static/
│   │   ├── scss/         # Sass source, compiled to css/app.css
│   │   ├── js/
│   │   ├── fonts/
│   │   ├── assets/       # Icons and images
│   │   └── uploads/      # Post media (not tracked in git)
│   ├── templates/        # Jinja templates (pages, components, macros, seo)
│   ├── extensions.py     # Database, login manager, rate limiter
│   └── __init__.py       # Application factory
├── deploy/               # Server config, deploy script, weekly report
├── migrations/           # Database migrations
├── scripts/              # Seed script
├── config.py
├── requirements.txt
└── run.py
```

*Shown to depth 3; some files omitted.*

## TODO
- Create / Implement a backup script

## License

MIT. See [LICENSE](LICENSE).
