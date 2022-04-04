from flask import Blueprint
from pathlib import Path
from app.upload import Uploader, Method
from app.local import Local
from app.exif import Exif
import click

bp = Blueprint("cli", __name__)


@bp.cli.command('upload_thumbs')
@click.argument("path")
def cmd_upload_thumbs(path):
    path = Path(path).absolute()
    if not path.exists():
        raise FileNotFoundError
    source = Path("processed")
    photos = list(map(lambda x: x.strip(), source.read_text().split("\n")))
    uploader = Uploader(len(photos), Method.THUMB)
    for f in photos:
        f = Path(f)
        src = f.absolute()
        dst = f.relative_to(path)
        uploader.add(src.as_posix(), dst.as_posix())


@bp.cli.command('upload')
@click.argument("path")
def cmd_upload(path):
    path = Path(path).absolute()
    if not path.exists():
        raise FileNotFoundError
    it = Local(path)
    uploader = Uploader(len(it))
    for f in it:
        src = f.absolute()
        dst = f.relative_to(path)
        uploader.add(src.as_posix(), dst.as_posix())
        break


@bp.cli.command('exif')
@click.argument("path")
def cmd_exif(path):
    path = Path(path).absolute()
    if not path.exists():
        raise FileNotFoundError
    it = Local(path)
    for f in it:
        ex = Exif(f)
        print(f, ex.timestamp, ex.width, ex.height)
        break
