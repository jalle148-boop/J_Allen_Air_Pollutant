"""Create a .venv and install requirements if missing.

Usage: run this file with your system Python from anywhere inside the repo.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for parent in [start, *start.parents]:
        if (parent / ".git").exists() or (parent / "requirements.txt").exists():
            return parent
    return start


def find_existing_venv(start: Path) -> Path | None:
    for parent in [start, *start.parents]:
        candidate = parent / ".venv"
        if candidate.exists() and candidate.is_dir():
            return candidate
    return None


def venv_python_path(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=str(cwd), check=True)


def main() -> int:
    start = Path.cwd()
    existing = find_existing_venv(start)
    if existing:
        print(f".venv already exists at: {existing}")
        return 0

    repo_root = find_repo_root(start)
    venv_dir = repo_root / ".venv"
    print(f"Creating .venv at: {venv_dir}")
    run([sys.executable, "-m", "venv", str(venv_dir)], cwd=repo_root)

    venv_python = venv_python_path(venv_dir)
    print("Upgrading pip...")
    run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"], cwd=repo_root)

    requirements = repo_root / "requirements.txt"
    if requirements.exists():
        print("Installing requirements...")
        run([str(venv_python), "-m", "pip", "install", "-r", str(requirements)], cwd=repo_root)
    else:
        print("No requirements.txt found. Skipping install.")

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())