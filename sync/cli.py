from pathlib import Path
from xml.dom import NotFoundErr
import click
import sys
from sync.local import Local
from sync.upload import Uploader


class SyncCommands(click.Group):
    def list_commands(self, ctx: click.Context) -> list[str]:
        return list(self.commands)


@click.group(cls=SyncCommands)
def cli():
    """This script showcases different terminal UI helpers in Click."""
    pass


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


@cli.command('quit', short_help="Quit")
def cmd_quit():
    """Quit."""
    click.echo(click.style("Bye!", fg='blue'))
    sys.exit(0)
