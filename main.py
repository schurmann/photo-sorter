import shutil
import sys
from collections import defaultdict
from pathlib import Path
from typing import Generator, DefaultDict

import exifread

ModelDict = DefaultDict[str, list[Path]]


def image_model(filename):
    with open(filename, 'rb') as f:
        exif_tags = exifread.process_file(f)
        return str(exif_tags.get('Image Model'))


def resolve_path(p: str):
    path = Path(p)
    return path.expanduser() if '~' in p else path.resolve()


def traverse_dir(p: Path) -> Generator[Path, None, None]:
    for path in p.rglob('*.jpg'):
        yield path


if __name__ == '__main__':
    try:
        in_dir, out_dir = sys.argv[1:3]
    except ValueError as e:
        print(f"Usage: {__file__} <input dir> <output dir>")
        exit(1)
    in_dir = resolve_path(in_dir)
    out_dir = resolve_path(out_dir)
    print(f"Input dir: {in_dir}\nOutput dir: {out_dir}")
    model_dict: ModelDict = defaultdict(list)
    for f in traverse_dir(in_dir):
        try:
            model = image_model(f)
        except Exception as e:
            print(e)
            continue
        if model is None:
            print(f"No model found for {f}")
            continue
        model_dict[model].append(f)

    print(f"Creating models dirs in {out_dir}")
    [(out_dir / model).mkdir(parents=True, exist_ok=True) for model in model_dict.keys()]
    for model, files in model_dict.items():
        print(f"Copying files for model {model}")
        print(f"{len(files)} files")
        for f in files:
            shutil.copy(f, (out_dir / model / f.name))
