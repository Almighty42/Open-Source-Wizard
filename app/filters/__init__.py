from .render import render_markdown, format_date, extract_headings, replace_arg

def register_filters(app):
    app.jinja_env.filters["markdown"] = render_markdown
    app.jinja_env.filters["date"] = format_date
    app.jinja_env.filters["extract_headings"] = extract_headings
    app.jinja_env.filters["replace"] = replace_arg
