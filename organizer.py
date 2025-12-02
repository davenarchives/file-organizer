"""Single-file CLI for organizing files into subfolders by type."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

# Mapping of category names to the file extensions they include.
CATEGORY_MAP: dict[str, set[str]] = {
    "Images": {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".tiff",
        ".webp",
        ".heic",
        ".svg",
    },
    "Documents": {
        ".pdf",
        ".doc",
        ".docx",
        ".txt",
        ".rtf",
        ".odt",
        ".md",
    },
    "Spreadsheets": {
        ".xls",
        ".xlsx",
        ".csv",
        ".ods",
        ".tsv",
    },
    "Presentations": {
        ".ppt",
        ".pptx",
        ".odp",
        ".key",
    },
    "Videos": {
        ".mp4",
        ".mkv",
        ".mov",
        ".avi",
        ".wmv",
        ".flv",
        ".webm",
        ".m4v",
    },
    "Audio": {
        ".mp3",
        ".wav",
        ".flac",
        ".aac",
        ".ogg",
        ".m4a",
        ".wma",
    },
    "Archives": {
        ".zip",
        ".rar",
        ".7z",
        ".tar",
        ".gz",
        ".bz2",
        ".xz",
    },
    "Code": {
        ".py",
        ".js",
        ".ts",
        ".java",
        ".c",
        ".cpp",
        ".cs",
        ".rb",
        ".go",
        ".php",
        ".sh",
        ".ps1",
        ".html",
        ".css",
        ".json",
        ".xml",
        ".yml",
        ".yaml",
    },
    "Executables": {
        ".exe",
        ".msi",
        ".bat",
        ".cmd",
    },
}

# Defaults: operate on Downloads by default and place categories there.
DEFAULT_SOURCE = Path.home() / "Downloads"
DEFAULT_TARGET_ROOT = DEFAULT_SOURCE


def pick_category(extension: str) -> str:
    """Return category name for an extension, defaulting to Other."""
    ext = extension.lower()
    for category, extensions in CATEGORY_MAP.items():
        if ext in extensions:
            return category
    return "Other"


def next_available_path(path: Path) -> Path:
    """Return a non-conflicting path by appending _<n> if needed."""
    if not path.exists():
        return path

    stem, suffix = path.stem, path.suffix
    parent = path.parent
    counter = 1
    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def organize(
    source: Path, target_root: Path, dry_run: bool, create_source: bool
) -> None:
    """Move files from source into categorized folders under target_root."""
    if not source.exists():
        if create_source:
            source.mkdir(parents=True, exist_ok=True)
            print(f"Created source folder: {source}")
        else:
            raise FileNotFoundError(f"Source folder not found: {source}")
    if not source.is_dir():
        raise NotADirectoryError(f"Source path is not a folder: {source}")

    for item in source.iterdir():
        if item.is_dir():
            continue

        category = pick_category(item.suffix)
        destination_dir = target_root / category
        destination_dir.mkdir(parents=True, exist_ok=True)

        destination_path = next_available_path(destination_dir / item.name)

        if dry_run:
            print(f"[dry-run] {item} -> {destination_path}")
        else:
            shutil.move(str(item), destination_path)
            print(f"Moved {item} -> {destination_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Organize files from a source folder into category subfolders"
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help=f"Path to the folder whose files you want to organize (default: {DEFAULT_SOURCE})",
    )
    parser.add_argument(
        "--target-root",
        type=Path,
        default=DEFAULT_TARGET_ROOT,
        help=(
            f"Where to create the category folders "
            f"(default: {DEFAULT_TARGET_ROOT})"
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be moved without moving files",
    )
    parser.add_argument(
        "--create-source",
        action="store_true",
        dest="create_source",
        help="Create the source folder if it does not exist",
    )
    parser.add_argument(
        "--no-create-source",
        action="store_false",
        dest="create_source",
        help="Do not create the source folder if it does not exist",
    )
    parser.set_defaults(create_source=True)

    args = parser.parse_args()
    organize(args.source, args.target_root, args.dry_run, args.create_source)


if __name__ == "__main__":
    main()
