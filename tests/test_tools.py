"""Tests for utility tools."""
import pytest
from src.tools import (
    json_validate, json_format,
    base64_encode, base64_decode,
    hash_generate, uuid_generate,
    text_stats, slug_generate, regex_test,
    url_parse,
    markdown_to_html, html_to_markdown,
    csv_to_json, json_to_csv,
    datetime_convert, cron_parse,
    diff_text, jwt_decode
)


def test_json_validate():
    result = json_validate('{"key": "value"}')
    assert result["success"] is True
    assert result["result"]["key"] == "value"
    
    result = json_validate('{invalid}')
    assert result["success"] is False


def test_json_format():
    result = json_format('{"b":1,"a":2}', minify=False)
    assert result["success"] is True
    assert '"a"' in result["result"]
    
    result = json_format('{"b":1,"a":2}', minify=True)
    assert result["success"] is True
    assert '\n' not in result["result"]


def test_base64():
    text = "Hello World"
    encoded = base64_encode(text)
    assert encoded["success"] is True
    
    decoded = base64_decode(encoded["result"])
    assert decoded["success"] is True
    assert decoded["result"] == text


def test_hash_generate():
    result = hash_generate("test", "sha256")
    assert result["success"] is True
    assert len(result["result"]) == 64  # SHA256 hex length
    
    result = hash_generate("test", "md5")
    assert result["success"] is True
    assert len(result["result"]) == 32  # MD5 hex length


def test_uuid_generate():
    result = uuid_generate(4)
    assert result["success"] is True
    assert len(result["result"]) == 36  # UUID string length with dashes


def test_text_stats():
    result = text_stats("Hello world. This is a test.")
    assert result["success"] is True
    assert result["result"]["words"] == 6
    assert result["result"]["sentences"] == 2


def test_slug_generate():
    result = slug_generate("Hello World! This is a Test.")
    assert result["success"] is True
    assert result["result"] == "hello-world-this-is-a-test"


def test_regex_test():
    result = regex_test(r'\d+', "abc 123 def 456")
    assert result["success"] is True
    assert result["result"]["count"] == 2
    assert "123" in result["result"]["matches"]


def test_url_parse():
    result = url_parse("https://example.com:8080/path?key=value#hash")
    assert result["success"] is True
    assert result["result"]["scheme"] == "https"
    assert result["result"]["hostname"] == "example.com"
    assert result["result"]["port"] == 8080
    assert result["result"]["path"] == "/path"


def test_markdown_to_html():
    result = markdown_to_html("# Hello\n\nWorld")
    assert result["success"] is True
    assert "<h1>" in result["result"]


def test_html_to_markdown():
    result = html_to_markdown("<h1>Hello</h1><p>World</p>")
    assert result["success"] is True
    assert "#" in result["result"]


def test_csv_json_conversion():
    csv_text = "name,age\nJohn,30\nJane,25"
    result = csv_to_json(csv_text)
    assert result["success"] is True
    assert len(result["result"]) == 2
    assert result["result"][0]["name"] == "John"
    
    # Convert back
    import json
    json_str = json.dumps(result["result"])
    result2 = json_to_csv(json_str)
    assert result2["success"] is True
    # Columns may be reordered (sorted alphabetically)
    assert "name" in result2["result"] and "age" in result2["result"]
    assert "John" in result2["result"] and "30" in result2["result"]


def test_datetime_convert():
    result = datetime_convert("2024-01-01 12:00:00", "UTC", "America/New_York")
    assert result["success"] is True
    assert "datetime" in result["result"]
    assert "timestamp" in result["result"]


def test_cron_parse():
    result = cron_parse("0 12 * * *", count=3)
    assert result["success"] is True
    assert len(result["result"]["next_runs"]) == 3


def test_diff_text():
    result = diff_text("Hello\nWorld", "Hello\nPython")
    assert result["success"] is True
    assert "diff" in result["result"]
    assert "similarity" in result["result"]


def test_jwt_decode():
    # Sample JWT (unverified)
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    result = jwt_decode(token)
    assert result["success"] is True
    assert result["result"]["payload"]["name"] == "John Doe"
