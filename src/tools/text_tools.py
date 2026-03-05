"""Text processing utility tools."""
import re
import unicodedata
from typing import Any, Dict


def text_stats(text: str) -> Dict[str, Any]:
    """Calculate text statistics (word count, char count, sentences, reading time)."""
    try:
        # Character count
        char_count = len(text)
        char_count_no_spaces = len(text.replace(' ', ''))
        
        # Word count
        words = text.split()
        word_count = len(words)
        
        # Sentence count (simple heuristic)
        sentences = re.split(r'[.!?]+', text)
        sentence_count = len([s for s in sentences if s.strip()])
        
        # Reading time (average 200 words per minute)
        reading_time_minutes = word_count / 200 if word_count > 0 else 0
        
        return {
            "success": True,
            "result": {
                "characters": char_count,
                "characters_no_spaces": char_count_no_spaces,
                "words": word_count,
                "sentences": sentence_count,
                "reading_time_minutes": round(reading_time_minutes, 2)
            }
        }
    except Exception as e:
        return {"success": False, "error": f"Error calculating text stats: {str(e)}"}


def slug_generate(text: str, separator: str = "-") -> Dict[str, Any]:
    """Generate URL-safe slug from text."""
    try:
        # Normalize unicode characters
        text = unicodedata.normalize('NFKD', text)
        text = text.encode('ascii', 'ignore').decode('ascii')
        
        # Convert to lowercase
        text = text.lower()
        
        # Replace spaces and special chars with separator
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[\s_-]+', separator, text)
        
        # Remove leading/trailing separators
        text = text.strip(separator)
        
        return {"success": True, "result": text}
    except Exception as e:
        return {"success": False, "error": f"Error generating slug: {str(e)}"}


def regex_test(pattern: str, text: str, flags: str = "") -> Dict[str, Any]:
    """Test regex pattern against text and return matches."""
    try:
        # Parse flags
        re_flags = 0
        if 'i' in flags.lower():
            re_flags |= re.IGNORECASE
        if 'm' in flags.lower():
            re_flags |= re.MULTILINE
        if 's' in flags.lower():
            re_flags |= re.DOTALL
        
        # Compile pattern
        compiled = re.compile(pattern, re_flags)
        
        # Find all matches
        matches = compiled.findall(text)
        
        # Also get match objects for more details
        match_objects = []
        for match in compiled.finditer(text):
            match_objects.append({
                "match": match.group(),
                "start": match.start(),
                "end": match.end(),
                "groups": match.groups()
            })
        
        return {
            "success": True,
            "result": {
                "matches": matches,
                "count": len(matches),
                "details": match_objects
            }
        }
    except re.error as e:
        return {"success": False, "error": f"Invalid regex pattern: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Error testing regex: {str(e)}"}
