"""
Generate .pyz archive for demo or examples
"""

from os import getcwd
from pathlib import Path
from shutil import copy2
from tempfile import TemporaryDirectory
import argparse
import zipapp


if __name__ == "__main__":
    cwd: Path = Path(getcwd())
    examples: list[str] = [f.name for f in Path(cwd / "examples").glob("*.py")]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-t", "--target",
        type=str,
        default="main.py",
        choices=["main.py", *examples],
        help="Which script should be executed (default: %(default)s)"
    )
    args = parser.parse_args()

    if not (exec_dir := Path(cwd / "exec")).exists():
        exec_dir.mkdir(exist_ok=True)

    with TemporaryDirectory() as td:
        td = Path(td) / "demo-python"
        for f in Path(".").rglob("*"):
            if str(f.resolve()) == __file__:
                continue
            if f.suffix == ".py":
                dst = td / f.parent
                dst.mkdir(parents=True, exist_ok=True)
                if f.name == args.target:
                    copy2(f, td / "__main__.py")
                else:
                    copy2(f, dst)
        exec_name = "demo_python" if args.target == "main.py" else Path(args.target).stem
        zipapp.create_archive(td, f"exec/{exec_name}.pyz")
