"""Cryptographic and encoding utility tools."""
import base64
import hashlib
import uuid
import jwt
from typing import Any, Dict


def base64_encode(text: str) -> Dict[str, Any]:
    """Encode string to base64."""
    try:
        encoded = base64.b64encode(text.encode('utf-8')).decode('utf-8')
        return {"success": True, "result": encoded}
    except Exception as e:
        return {"success": False, "error": f"Error encoding to base64: {str(e)}"}


def base64_decode(encoded: str) -> Dict[str, Any]:
    """Decode base64 string."""
    try:
        decoded = base64.b64decode(encoded).decode('utf-8')
        return {"success": True, "result": decoded}
    except Exception as e:
        return {"success": False, "error": f"Error decoding base64: {str(e)}"}


def hash_generate(text: str, algorithm: str = "sha256") -> Dict[str, Any]:
    """Generate hash of input text (md5, sha256, sha512)."""
    try:
        algorithm = algorithm.lower()
        if algorithm == "md5":
            hash_obj = hashlib.md5(text.encode('utf-8'))
        elif algorithm == "sha256":
            hash_obj = hashlib.sha256(text.encode('utf-8'))
        elif algorithm == "sha512":
            hash_obj = hashlib.sha512(text.encode('utf-8'))
        else:
            return {"success": False, "error": f"Unsupported algorithm: {algorithm}. Use md5, sha256, or sha512"}
        
        return {"success": True, "result": hash_obj.hexdigest()}
    except Exception as e:
        return {"success": False, "error": f"Error generating hash: {str(e)}"}


def uuid_generate(version: int = 4) -> Dict[str, Any]:
    """Generate UUID (v4 or v7)."""
    try:
        if version == 4:
            generated = str(uuid.uuid4())
        elif version == 7:
            # UUID v7 is time-ordered (Python 3.11+)
            try:
                generated = str(uuid.uuid7())
            except AttributeError:
                return {"success": False, "error": "UUID v7 requires Python 3.11+"}
        else:
            return {"success": False, "error": f"Unsupported UUID version: {version}. Use 4 or 7"}
        
        return {"success": True, "result": generated}
    except Exception as e:
        return {"success": False, "error": f"Error generating UUID: {str(e)}"}


def jwt_decode(token: str) -> Dict[str, Any]:
    """Decode JWT payload (no verification, for inspection only)."""
    try:
        # Decode without verification
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        # Also extract header
        header = jwt.get_unverified_header(token)
        
        return {
            "success": True,
            "result": {
                "header": header,
                "payload": decoded
            }
        }
    except jwt.DecodeError as e:
        return {"success": False, "error": f"Invalid JWT: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Error decoding JWT: {str(e)}"}
