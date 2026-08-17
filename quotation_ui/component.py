from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit.components.v1 as components

_BUILD_DIR = Path(__file__).resolve().parent / "build"

if not _BUILD_DIR.exists():
    raise RuntimeError(
        f"Quotation UI build is missing at {_BUILD_DIR}. The ZIP should already contain it. "
        "If you changed frontend source, run npm install && npm run build inside quotation_ui/frontend."
    )

_component = components.declare_component("mercedes_quotation_ui", path=str(_BUILD_DIR))


def render_quotation_ui(**kwargs: Any):
    return _component(default=None, **kwargs)
