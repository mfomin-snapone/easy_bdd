"""Pytest configuration for Easy BDD tests.

Sets up sys.path to include the project root and frontend directory
so that frontend modules can import from builder_core and other siblings.
"""

import sys
from pathlib import Path

# Add project root and frontend directory to sys.path so frontend modules
# can use their relative imports (e.g., "from builder_core import CATALOG")
ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(FRONTEND))
