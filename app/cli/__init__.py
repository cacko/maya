from flask import Blueprint
from app.storage import Storage
from pathlib import Path
from app.upload import Uploader
from app.storage.models.photo import  Photo
from app.local import Local
from app.exif import Exif
import click
from app.face.train import Train
from app.face.recognise import Recognise
from PIL import Image
from app.storage.models.face import Face
from app.storage.models.photo_face import PhotoFace
import pickle
from hashlib import blake2s
from app.core.image import show_tagged, save_tagged
from datetime import datetime
from app.core.progress import Progress
from tqdm import tqdm
from peewee import fn

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
            preserve=[Photo.latitude, Photo.longitude, Photo.folder,
                      Photo.full, Photo.thumb, Photo.timestamp],
            update={Photo.width: ex.width, Photo.height: ex.height}).execute()


@bp.cli.command('reprocess')
@click.argument("root")
@click.argument("lst")
def cmd_reprocess(root: str, lst: str):
    root = Path(root).resolve().absolute()
    path = Path(lst).resolve()
    if not path.exists():
        raise FileNotFoundError
    it = list(filter(lambda x: x.is_file(), map(
        lambda p: Path(p.strip()), path.read_text().split("\n"))))
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


@bp.cli.command('train')
@click.option("-w", "--overwrite", is_flag=True, default=False)
def cmd_train(overwrite):
    with Storage.db.atomic():
        for face_data in Train.train:
            args = {
                'name': face_data.name,
                'image': pickle.dumps(face_data.image),
                'encoding': pickle.dumps(face_data.encodings),
                'is_trained': True,
                'hash': Face.get_hash(face_data.image)
            }
            if overwrite:
                Face.insert(**args).on_conflict(
                    conflict_target=[Face.hash],
                    preserve=[Face.image, Face.is_trained, Face.name],
                    update={Face.encoding: pickle.dumps(face_data.encodings)}
                ).execute()
            else:
                Face.insert(**args).on_conflict_ignore().execute()


@bp.cli.command('self-train')
@click.argument("path")
def cmd_self_train(path):
    Recognise.register(Face.get_matched_data())
    path = Path(path)
    img_iterator = [path] if path.is_file() else Local(path)
    for img_path in tqdm(img_iterator):
        res = Recognise.faces(img_path, True)
        if not len(res):
            continue
        for m in res:
            with open(m.src, "rb") as img_fp:
                img = Image.open(img_fp)
                img.thumbnail(Recognise.SIZE)
                upper, right, lower, left = m.location
                sample = img.crop((left, upper, right, lower))
                h = blake2s(digest_size=20)
                h.update(m.src.encode())
                sample.save(f"{m.name}_{h.hexdigest()}.jpg", "jpeg")


@bp.cli.command('tag')
@click.argument("path")
@click.option("-f", "--find-matches", default=None)
@click.option("-t", "--tolerance", default=0.4)
@click.option("-q", "--quiet", is_flag=True, default=False)
def cmd_tag(path, find_matches, tolerance, quiet):
    Recognise.register(Face.get_matched_data())
    path = Path(path)
    img_iterator = [path] if path.is_file() else Local(path)
    results_path = Path(".") / f"results-{datetime.now().isoformat()}"
    if find_matches:
        find_matches = list(
            map(lambda n: n.strip().lower(), find_matches.split(",")))
        print(f"Matching only {','.join(find_matches)}")
    for img_path in tqdm(img_iterator):
        res = Recognise.faces(img_path, True, tolerance=tolerance)
        if len(res):
            names = [r.name for r in res]
            if find_matches and len(list(set(find_matches) & set(names))) == 0:
                continue
            if quiet:
                save_tagged(res, results_path)
            else:
                show_tagged(res)
    if quiet:
        print(f"All done, results are in {results_path.resolve()}")


@bp.cli.command('faces')
@click.argument("path")
@click.option("-t", "--tolerance", default=0.4)
@click.option("-r", "--save-results", is_flag=True, default=False)
@click.option("-b", "--batch-size", type=int, default=10)
@click.option("-w", "--overwrite", is_flag=True, default=False)
def cmd_faces(path, tolerance=0.4, save_results=False, batch_size=10, overwrite=False):
    Recognise.register(Face.get_matched_data())
    path = Path(path)
    batch: list[Photo] = []
    q = Photo.select()
    if not overwrite:
        q = q.where(Photo.processed == False)
    total_photos = q.count()
    progress = Progress(total=total_photos, desc="Photos")
    for record in q.iterator():
        total_photos -= 1
        batch.append(record)
        if len(batch) < batch_size and total_photos > 0:
            continue
        processed = []
        for res, photo in Recognise.batch_faces(
                path,
                batch,
                with_tags=save_results,
                tolerance=tolerance
        ):
            if len(res) > 0:
                matched = [{"photo_id": m.photo_id, "face_id": m.face_id}
                           for m in res]
                with Storage.db.atomic():
                    for pf in matched:
                        PhotoFace.insert(**pf).on_conflict_ignore().execute()
                    Photo.update(processed=True).where(Photo.id.in_([r.id for r in batch])).execute()
            if photo.id not in processed:
                processed.append(photo.id)
                progress.update()
        batch = []


@bp.cli.command("find")
@click.argument("name")
def cmd_find(name):
    res = (Photo
           .select(Photo.full, Photo.folder)
           .join(PhotoFace)
           .join(Face)
           .where(Face.name == name))
    for rec in res.dicts().iterator():
        print(rec)


@bp.cli.command("with-faces")
def cmd_with_faces():
    res = (Photo
           .select(Photo.full, Photo.folder, fn.STRING_AGG(Face.name, ","))
           .join(PhotoFace)
           .join(Face))
    for rec in res.dicts().iterator():
        print(rec)


@bp.cli.command("db_init")
def cmd_db_init():
    from app.storage.models import Photo, Face, PhotoFace
    with Storage.db as db:
        db.create_tables([Photo, Face, PhotoFace])
