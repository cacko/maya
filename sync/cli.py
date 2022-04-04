from pathlib import Path
from xml.dom import NotFoundErr
import click
import sys
from sync.local import Local
from sync.upload import Uploader, Method
from sync.exif import Exif


class SyncCommands(click.Group):
    def list_commands(self, ctx: click.Context) -> list[str]:
        return list(self.commands)


@click.group(cls=SyncCommands)
def cli():
    """This script showcases different terminal UI helpers in Click."""
    pass


@cli.command('upload_thumbs')
@click.argument("path")
def cmd_upload_thumbs(path):
    path = Path(path).absolute()
    if not path.exists():
        raise NotFoundErr
    source = Path("processed")
    photos = list(map(lambda x: x.strip(), source.read_text().split("\n")))
    uploader = Uploader(len(photos), Method.THUMB)
    for f in photos:
        f = Path(f)
        src = f.absolute()
        dst = f.relative_to(path)
        uploader.add(src.as_posix(), dst.as_posix())


@cli.command('upload')
@click.argument("path")
def cmd_upload(path):
    path = Path(path).absolute()
    if not path.exists():
        raise NotFoundErr
    it = Local(path)
    uploader = Uploader(len(it))
    for f in it:
        src = f.absolute()
        dst = f.relative_to(path)
        uploader.add(src.as_posix(), dst.as_posix())
        break


@cli.command('exif')
@click.argument("path")
def cmd_exif(path):
    path = Path(path).absolute()
    if not path.exists():
        raise NotFoundErr
    it = Local(path)
    for f in it:
        ex = Exif(f)
        print(f, ex.timestamp, ex.width, ex.height)


@cli.command('quit', short_help="Quit")
def cmd_quit():
    """Quit."""
    click.echo(click.style("Bye!", fg='blue'))
    sys.exit(0)
