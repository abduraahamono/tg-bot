"""
Storage Utilities:
Provides atomic, corruption-proof JSON file reading and writing.
Prevents JSONDecodeError and race conditions using atomic rename (os.replace).
"""

import os
import json
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

def atomic_save_json(filepath: str | Path, data: Any) -> bool:
    """
    Saves JSON data atomically using a temporary file and os.replace.
    Guarantees the file is never left in a corrupted/half-written state.
    """
    p = Path(filepath).resolve()
    p.parent.mkdir(parents=True, exist_ok=True)
    temp_path = p.with_name(f".{p.name}.tmp")
    
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, p)
        return True
    except Exception as e:
        print(f"[atomic_save_json] Error saving to {p}: {e}")
        if temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass
        return False

def safe_load_json(filepath: str | Path, default: Optional[Any] = None) -> Any:
    """
    Safely reads JSON data, returning default if file doesn't exist or is invalid.
    """
    p = Path(filepath).resolve()
    if not p.exists():
        return default if default is not None else {}
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[safe_load_json] Error loading {p}: {e}")
        return default if default is not None else {}
