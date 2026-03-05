"""Conversion utility tools."""
import csv
import io
import json
from datetime import datetime
from typing import Any, Dict
import markdown
from markdownify import markdownify
from dateutil import parser as date_parser, tz
from croniter import croniter, CroniterBadCronError


def markdown_to_html(md_text: str) -> Dict[str, Any]:
    """Convert markdown to HTML."""
    try:
        html = markdown.markdown(md_text, extensions=['extra', 'codehilite'])
        return {"success": True, "result": html}
    except Exception as e:
        return {"success": False, "error": f"Error converting markdown to HTML: {str(e)}"}


def html_to_markdown(html_text: str) -> Dict[str, Any]:
    """Convert HTML to markdown."""
    try:
        md = markdownify(html_text, heading_style="ATX")
        return {"success": True, "result": md}
    except Exception as e:
        return {"success": False, "error": f"Error converting HTML to markdown: {str(e)}"}


def csv_to_json(csv_text: str, delimiter: str = ",") -> Dict[str, Any]:
    """Convert CSV to JSON."""
    try:
        reader = csv.DictReader(io.StringIO(csv_text), delimiter=delimiter)
        result = list(reader)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": f"Error converting CSV to JSON: {str(e)}"}


def json_to_csv(json_data: str, delimiter: str = ",") -> Dict[str, Any]:
    """Convert JSON to CSV."""
    try:
        # Parse JSON
        data = json.loads(json_data)
        
        # Ensure it's a list
        if not isinstance(data, list):
            return {"success": False, "error": "JSON must be an array of objects"}
        
        if not data:
            return {"success": True, "result": ""}
        
        # Get all unique keys from all objects
        all_keys = set()
        for item in data:
            if isinstance(item, dict):
                all_keys.update(item.keys())
        
        fieldnames = sorted(all_keys)
        
        # Write CSV
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(data)
        
        return {"success": True, "result": output.getvalue()}
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"Invalid JSON: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Error converting JSON to CSV: {str(e)}"}


def datetime_convert(
    dt_string: str,
    from_tz: str = "UTC",
    to_tz: str = "UTC",
    from_format: str = None,
    to_format: str = None
) -> Dict[str, Any]:
    """Convert datetime between timezones and formats."""
    try:
        # Parse datetime
        if from_format:
            dt = datetime.strptime(dt_string, from_format)
        else:
            # Try to parse automatically
            dt = date_parser.parse(dt_string)
        
        # If datetime is naive, assume it's in from_tz
        if dt.tzinfo is None:
            from_tzinfo = tz.gettz(from_tz)
            dt = dt.replace(tzinfo=from_tzinfo)
        
        # Convert to target timezone
        to_tzinfo = tz.gettz(to_tz)
        dt_converted = dt.astimezone(to_tzinfo)
        
        # Format output
        if to_format:
            result_str = dt_converted.strftime(to_format)
        else:
            result_str = dt_converted.isoformat()
        
        return {
            "success": True,
            "result": {
                "datetime": result_str,
                "timestamp": int(dt_converted.timestamp()),
                "timezone": to_tz
            }
        }
    except Exception as e:
        return {"success": False, "error": f"Error converting datetime: {str(e)}"}


def cron_parse(cron_expression: str, count: int = 5) -> Dict[str, Any]:
    """Parse cron expression and show next run times."""
    try:
        # Validate cron expression
        cron = croniter(cron_expression, datetime.now())
        
        # Get next N run times
        next_runs = []
        for _ in range(count):
            next_run = cron.get_next(datetime)
            next_runs.append(next_run.isoformat())
        
        # Generate human-readable description (basic)
        parts = cron_expression.split()
        if len(parts) < 5:
            description = "Invalid cron expression (needs at least 5 parts)"
        else:
            minute, hour, day, month, weekday = parts[:5]
            description = f"Runs at minute {minute}, hour {hour}, day {day}, month {month}, weekday {weekday}"
        
        return {
            "success": True,
            "result": {
                "expression": cron_expression,
                "description": description,
                "next_runs": next_runs
            }
        }
    except CroniterBadCronError as e:
        return {"success": False, "error": f"Invalid cron expression: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Error parsing cron: {str(e)}"}
