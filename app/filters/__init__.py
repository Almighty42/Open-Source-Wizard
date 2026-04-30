from .render import render_markdown, format_date, extract_headings

def register_filters(app):
    app.jinja_env.filters["markdown"] = render_markdown
    app.jinja_env.filters["date"] = format_date
    app.jinja_env.filters["extract_headings"] = extract_headings
