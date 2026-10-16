<div align="center">
  <img width="510" height="150" alt="Open Source Wizard logo" src="https://github.com/user-attachments/assets/aae04c99-998d-4182-8684-85c00b7b72fe" />

  **Source code for [opensourcewizard.com](https://opensourcewizard.com), a blog about embedded systems, electronics and DIY hardware.**

  ![Python](https://img.shields.io/badge/python-3.12+-blue) ![Flask](https://img.shields.io/badge/flask-3.1-black) ![License](https://img.shields.io/badge/license-MIT-green)
</div>

<img width="1366" height="696" alt="Screenshot of the homepage" src="https://github.com/user-attachments/assets/2f382152-9657-4c98-b28f-7dc6aca214c5" />

## Features

- Write articles and projects in Markdown, with syntax-highlighted code blocks and sanitized HTML output
- Tags, categories, and attached images, videos and files for every post
- Admin panel for writing, editing and publishing content
- Light and dark theme
- Rate limiting and account lockout on login

## Tech stack

- **Backend:** Python, Flask
- **Database:** SQLite
- **Frontend:** Jinja templates, Sass, vanilla JavaScript
- **Hosting:** DigitalOcean, Cloudflare

## Run locally

todo...

## Deployment

The site is hosted on DigitalOcean behind Cloudflare. Server setup, configuration and troubleshooting are documented in [deploy/DEPLOY.md](deploy/DEPLOY.md).

Updating the live site from your machine:

```bash
git push                    # commit your changes to main first
deploy/deploy.sh            # deploy what's already pushed
deploy/deploy.sh --push     # push local commits, then deploy
```

The script pulls the new code on the server, installs changed dependencies, backs up and migrates the database when migrations changed, restarts the service and checks that the site responds. If a step fails, it rolls the code back to the previous commit.

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
├── deploy/               # Server config, deploy script, runbook
├── migrations/           # Database migrations
├── scripts/              # Seed script
├── config.py
├── requirements.txt
└── run.py
```

*Shown to depth 3; some files omitted.*

## TODO
- Create / Implement a backup script
- Create / Implement a info / error log script for informing the administrator

## License

MIT. See [LICENSE](LICENSE).
