"""
Os scripts rodam no host, fora do container, e não importam nada de `app`.
Isto só coloca a pasta `scripts/` no caminho de import.
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(RAIZ / "scripts"))
