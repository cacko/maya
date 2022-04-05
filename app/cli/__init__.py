from flask import Blueprint
from pathlib import Path
from app.upload import Uploader
from app.storage import Storage
from app.storage.models import Photo
from app.local import Local
from app.exif import Exif
import click
from tqdm import tqdm

bp = Blueprint("cli", __name__)


def post_upload(folder, src, full, thumb):
    ex = Exif(Path(src))
    with Storage.db.atomic():
        Photo.insert(
            folder=folder,
            full=full,
            thumb=thumb,
            timestamp=ex.timestamp,
            width=ex.width,
            height=ex.height,
            latitude=ex.gps.latitude,
            longitude=ex.gps.longitude
        ).on_conflict(
            conflict_target=[Photo.full],
            preserve=[Photo.latitude, Photo.longitude, Photo.folder, Photo.full, Photo.thumb, Photo.timestamp],
            update={Photo.width: ex.width, Photo.height: ex.height}).execute()


@bp.cli.command('reprocess')
@click.argument("root")
@click.argument("lst")
def cmd_reprocess(root: str, lst: str):
    root = Path(root).resolve().absolute()
    path = Path(lst).resolve()
    if not path.exists():
        raise FileNotFoundError
    it = list(filter(lambda x: x.is_file(), map(lambda p: Path(p.strip()), path.read_text().split("\n"))))
    uploader = Uploader(len(it), callback=post_upload)
    for f in it:
        src = f.absolute()
        dst = f.relative_to(root)
        uploader.add(src.as_posix(), dst.as_posix())


@bp.cli.command('process')
@click.argument("path")
def cmd_process(path):
    path = Path(path).resolve()
    if not path.exists():
        raise FileNotFoundError
    it = Local(path)
    uploader = Uploader(len(it), callback=post_upload)
    for f in it:
        src = f.absolute()
        dst = f.relative_to(path)
        uploader.add(src.as_posix(), dst.as_posix())


@bp.cli.command('orientation')
@click.argument("path")
def cmd_orientation(path):
    path = Path(path).resolve()
    if not path.exists():
        raise FileNotFoundError
    it = Local(path)
    output = Path(".") / "reprocess"
    with output.open("w") as fp:
        for f in tqdm(it):
            ex = Exif(f)
            if ex.fix_orientation():
                fp.write(f"{f}\n")


@bp.cli.command("dbinit")
def cmd_dbinit():
    from app.storage.models import Photo
    with Storage.db as db:
        db.create_tables([Photo])
