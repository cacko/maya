from curses.ascii import HT
from bottle import route, run, static_file
from pathlib import Path

HTDOCS_ROOT = Path(".").parent.parent / "public"

@route('/')
def homepage():
    return static_file("index.html", root=HTDOCS_ROOT.absolute().as_posix())


@route('/<filename>')
def server_static(filename):
    return static_file(filename, root=HTDOCS_ROOT.absolute().as_posix())


run(host='localhost', port=12018, debug=True)