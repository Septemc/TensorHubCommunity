from app.utils.markdown import sanitize_markdown


def test_sanitize_markdown_strips_script_tags() -> None:
    raw = "# Title\n\n<script>alert('x')</script><b>safe</b>"
    result = sanitize_markdown(raw)
    assert '<script>' not in result
    assert '<b>safe</b>' in result
