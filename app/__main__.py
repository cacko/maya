from curses.ascii import HT
from bottle import route, run, static_file
from pathlib import Path

HTDOCS_ROOT = Path(".").parent.parent / "public"

@route('/')
def homepage():
    return static_file("index.html", root=HTDOCS_ROOT.absolute().as_posix())


@route('/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root=HTDOCS_ROOT.absolute().as_posix())


run(host='0.0.0.0', port=12018, debug=True)