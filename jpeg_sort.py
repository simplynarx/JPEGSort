#!/usr/bin/env python3

import os
import shutil
import sys
from PIL import Image
from PIL.ExifTags import TAGS
from rich.progress import SpinnerColumn, TextColumn, Progress

# Map tag names to EXIF keys
tag_map = {v: k for k, v in TAGS.items()}

def image_sort(working_dir: str) -> None:
    """
    Sorts all files in the working directory:
    - .jpg/.jpeg files are sorted into folders by year (from EXIF metadata)
    - All others go into 'Unsorted'
    Uses a spinner + progress display while copying files.
    """

    all_files = []

    # Walk through all files in the working directory
    for root, dirs, files in os.walk(working_dir, topdown=False):
        for name in files:
            file_path = os.path.join(root, name)
            all_files.append(file_path)

    total = len(all_files)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TextColumn("{task.completed} / {task.total}"),
    ) as progress:
        task = progress.add_task("Sorting and copying files...", total=total)

        for file_path in all_files:
            filename = os.path.basename(file_path)

            # Checks if the filename contains a valid extension
            if check_valid(filename):
                year = get_year(file_path)
                dest_dir = os.path.join(output_dir, year)
            else:
                dest_dir = os.path.join(output_dir, "Unsorted")

            os.makedirs(dest_dir, exist_ok=True)

            # Resolve duplicates
            safe_name = resolve_duplicate(dest_dir, filename)
            dest_path = os.path.join(dest_dir, safe_name)

            try:
                shutil.copy(file_path, dest_path)
            except Exception:
                pass

            progress.advance(task)


def check_valid(name: str) -> bool:
    """
    Checks if a file has a .jpg or .jpeg extension.

    Args:
        name (str): File name

    Returns:
        bool: True if extension is valid
    """

    _, ext = os.path.splitext(name)
    return ext.lower() in [".jpg", ".jpeg"]


def get_year(filepath: str) -> str:
    """
    Extracts the year from EXIF metadata of a JPEG file.

    Args:
        filepath (str): Path to image file

    Returns:
        str: Year as a 4-digit string, or "Unsorted" if missing
    """

    try:
        image = Image.open(filepath)
        exif_data = image._getexif()

        if exif_data and tag_map.get("DateTime") in exif_data:
            datetime_str = exif_data[tag_map["DateTime"]]
            return datetime_str[:4]  # First 4 chars = year
    except Exception:
        pass

    return "Unsorted"


def resolve_duplicate(dest_dir: str, filename: str) -> str:
    """
    If a file with the same name already exists in dest_dir,
    appends _1, _2, etc. to make it unique.

    Args:
        dest_dir (str): Destination directory path
        filename (str): Original file name

    Returns:
        str: A unique file name in the destination directory
    """

    base, ext = os.path.splitext(filename)
    counter = 1
    candidate = filename

    while os.path.exists(os.path.join(dest_dir, candidate)):
        candidate = f"{base}_{counter}{ext}"
        counter += 1

    return candidate


if __name__ == "__main__":
    argc = len(sys.argv)
    working_dir = "."
    output_dir = os.path.join(working_dir, "Output")

    if argc >= 2 and sys.argv[1] in ["-h", "--help"]:
        sys.stderr.write(
            "Usage:  jpeg_sort.py\n"
            "\tjpeg_sort.py [working_directory]\n"
            "\tjpeg_sort.py [working_directory] [output_directory]\n\n"
            "The default working directory is '.'\n"
            "The default output directory is './Output'\n"
        )
        exit()

    if argc == 2:
        working_dir = sys.argv[1]
        output_dir = os.path.join(working_dir, "Output")
    elif argc == 3:
        working_dir = sys.argv[1]
        output_dir = sys.argv[2]
    elif argc > 3:
        sys.stderr.write(
            "Usage:  jpeg_sort.py\n"
            "\tjpeg_sort.py [working_directory]\n"
            "\tjpeg_sort.py [working_directory] [output_directory]\n\n"
            "The default working directory is '.'\n"
            "The default output directory is './Output'\n"
        )
        exit()

    image_sort(working_dir)
