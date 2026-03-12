import bleach
import markdown


ALLOWED_TAGS = [
    "a",
    "abbr",
    "acronym",
    "b",
    "blockquote",
    "code",
    "em",
    "i",
    "li",
    "ol",
    "p",
    "pre",
    "strong",
    "ul",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
]
ALLOWED_ATTRIBUTES = {"a": ["href", "title", "target", "rel"]}


def sanitize_markdown(raw_text: str) -> str:
    html = markdown.markdown(raw_text, extensions=["extra", "tables", "fenced_code"])
    return bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)
