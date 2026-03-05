"""Diff utility tools."""
import difflib
from typing import Any, Dict


def diff_text(text1: str, text2: str, context_lines: int = 3) -> Dict[str, Any]:
    """Compute unified diff between two text inputs."""
    try:
        # Split into lines
        lines1 = text1.splitlines(keepends=True)
        lines2 = text2.splitlines(keepends=True)
        
        # Generate unified diff
        diff = difflib.unified_diff(
            lines1,
            lines2,
            fromfile='text1',
            tofile='text2',
            lineterm='',
            n=context_lines
        )
        
        diff_text = '\n'.join(diff)
        
        # Also calculate similarity ratio
        similarity = difflib.SequenceMatcher(None, text1, text2).ratio()
        
        return {
            "success": True,
            "result": {
                "diff": diff_text,
                "similarity": round(similarity, 4)
            }
        }
    except Exception as e:
        return {"success": False, "error": f"Error computing diff: {str(e)}"}
