#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APPS = [
    ("strc", "fetch_strc.py"),
    ("bitcoin", "fetch_bitcoin.py"),
]


def main() -> int:
    failures = []
    for directory, script in APPS:
        cwd = ROOT / directory
        print(f"\n=== Running {directory}/{script} ===")
        result = subprocess.run([sys.executable, script], cwd=cwd)
        if result.returncode != 0:
            failures.append(f"{directory}/{script} (exit {result.returncode})")

    if failures:
        print("\nFailed:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("\nAll scripts completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
