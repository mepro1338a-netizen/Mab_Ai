"""Fix mojibake in active Python source files (UTF-8 double-decode)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {"archive", ".git", "__pycache__", "tools"}

MARKERS = ("Ã", "â€", "â‚¬", "ï¸", "ðŸ", "âš", "â–", "â¬", "â†", "âœ", "â", "â", "Ã")


def fix_line(line: str) -> str:
    if not any(marker in line for marker in MARKERS):
        return line
    try:
        return line.encode("latin-1").decode("utf-8")
    except UnicodeError:
        return line


def fix_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    fixed = original
    changed = True
    while changed:
        changed = False
        lines = fixed.splitlines(keepends=True)
        new_lines = [fix_line(line) for line in lines]
        new_fixed = "".join(new_lines)
        if new_fixed != fixed:
            fixed = new_fixed
            changed = True
    if fixed != original:
        path.write_text(fixed, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = []
    for path in ROOT.rglob("*.py"):
        if any(part in SKIP for part in path.parts):
            continue
        if fix_file(path):
            changed.append(str(path.relative_to(ROOT)))
    print(f"fixed {len(changed)} files")
    for name in changed:
        print(f"  - {name}")


if __name__ == "__main__":
    main()
