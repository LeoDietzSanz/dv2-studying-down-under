"""Run every prep script in order:   python prep/build.py

Each script validates its own output and exits with an error if a check
fails. This stops at the first failure, so later scripts never build on
bad data. Use it after re-downloading any raw file.
"""
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
STEPS = ["10_basic.py", "20_detailed.py", "30_higher_ed.py", "50_lookups.py"]

t0 = time.time()
for step in STEPS:
    print(f"\n{'=' * 60}\n{step}\n{'=' * 60}")
    result = subprocess.run([sys.executable, str(HERE / step)], cwd=HERE.parent)
    if result.returncode != 0:
        print(f"\nStopped: {step} failed. Fix it before running the rest.")
        sys.exit(result.returncode)

print(f"\nAll {len(STEPS)} prep scripts passed in {time.time() - t0:.0f}s. data/ is up to date.")
