ALLOWED_TAGS = [
    "p", "h1", "h2", "h3", "h4", "h5", "h6",
    "ul", "ol", "li", "blockquote", "pre", "code",
    "strong", "em", "a", "img", "hr", "br", "table",
    "thead", "tbody", "tr", "th", "td", "div", "span",   
    "svg", "circle", "line", "path", "rect",
    "button", "rect", "path",  "defs", "clipPath", "g",
    "linearGradient", "stop"
]

ALLOWED_ATTRIBUTES = {
        "h1": ["id"],
    "a": ["href", "title"],
    "img": ["src", "alt", "title", "width", "height"],
    "code": ["class"],
    "td": ["align"],
    "th": ["align"],
    "div": ["class", "role", "data-copy"],
    "span": ["class"],
    "svg": ["xmlns", "width", "height", "viewBox", "fill", "stroke",  "clip-path"
            "stroke-width", "stroke-linecap", "stroke-linejoin"],
    "g": ["clip-path"],
    "clipPath": ["id"],
    "circle": ["cx", "cy", "r"],
    "line": ["x1", "y1", "x2", "y2"],
    "button": ["class", "aria-label", "data-copy"],
    "rect": ["x", "y", "width", "height", "rx", "ry", "fill"],
    "path": ["d", "stroke", "stroke-width", "stroke-linecap", "stroke-linejoin",
             "fill", "fill-rule", "clip-rule"],
    "linearGradient": ["id", "x1", "y1", "x2", "y2", "gradientUnits"],
    "stop": ["offset", "stop-color", "stop-opacity"],
}
