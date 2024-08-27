from pathlib import Path
from shutil import copy2
from tempfile import TemporaryDirectory
import zipapp


if __name__ == "__main__":
    with TemporaryDirectory() as td:
        td = Path(td) / "demo-python"
        for f in Path(".").rglob("*"):
            if str(f.resolve()) == __file__:
                continue
            if f.suffix == ".py":
                dst = td / f.parent
                dst.mkdir(parents=True, exist_ok=True)
                if f.name == "main.py":
                    copy2(f, dst / "__main__.py")
                else:
                    copy2(f, dst)
        zipapp.create_archive(td, "demo-python.pyz")
