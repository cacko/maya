from flask import Blueprint
from peewee import fn

from app.storage import Storage
from pathlib import Path
from app.upload import Uploader
from app.storage.models import Photo
from app.local import Local
from app.exif import Exif
import click
from app.face.train import Train
from app.face.recognise import Recognise
from app.face.models import MatchData
from tqdm import tqdm
import face_recognition
import numpy as np
from PIL import Image, ImageDraw, ImageOps
from app.storage.models import Face, PhotoFace
import pickle
from io import BytesIO
from hashlib import blake2s

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


@bp.cli.command('train')
def cmd_train():
    with Storage.db.atomic():
        for face_data in Train.data:
            Face.insert(
                name=face_data.name,
                image=pickle.dumps(face_data.image),
                encoding=pickle.dumps(face_data.encodings),
                is_trained=True,
                hash=Face.get_hash(face_data.image)
            ).on_conflict_ignore().execute()


@bp.cli.command('tag')
@click.argument("path")
def cmd_tag(path):
    matched_data = [MatchData(
        encodings=pickle.loads(record.encoding),
        name=record.name,
        face_id=record.id
    ) for record in (Face.select())]
    Recognise.register(matched_data)
    path = Path(path)
    res = Recognise.faces(path, True)
    if len(res):
        names = ", ".join([r.name for r in res])
        buff = BytesIO(res[0].tagged)
        buff.seek(0)
        image = Image.open(buff)
        image.show()
        print(names)


@bp.cli.command('faces')
@click.argument("path")
def cmd_faces(path):
    known_face_encodings = []
    known_face_names = []
    known_face_id = []
    for record in (Face.select()):
        known_face_encodings.append(pickle.loads(record.encoding))
        known_face_names.append(record.name)
        known_face_id.append(record.id)

    path = Path(path)
    frames = []
    matched = []
    total_photos = Photo.select().count()
    progress = tqdm(total=total_photos)
    for photo in Photo.select().iterator():
        f = path / photo.full
        unknown_image = face_recognition.load_image_file(f.resolve().as_posix())
        img = Image.fromarray(unknown_image)
        img = ImageOps.pad(img, (500, 500))
        unknown_image = np.asarray(img)
        if len(frames) < 10 and total_photos:
            frames.append((photo, unknown_image))
            total_photos -= 1
            progress.update()
            if total_photos:
                continue
        batch_of_face_locations = face_recognition.batch_face_locations([f[1] for f in frames])
        for frame_number_in_batch, face_locations in enumerate(batch_of_face_locations):
            record = frames[frame_number_in_batch][0]
            unknown_image = frames[frame_number_in_batch][1]
            # pil_image = Image.fromarray(unknown_image)
            # draw = ImageDraw.Draw(pil_image)
            face_encodings = face_recognition.face_encodings(unknown_image, face_locations)
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                # name = "Unknown"
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    # name = known_face_names[best_match_index]
                    face_id = known_face_id[best_match_index]
                    matched.append({
                        'photo_id': record.id,
                        'face_id': face_id
                    })
                # draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255))
                # text_width, text_height = draw.textsize(name)
                # draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(0, 0, 255),
                #                outline=(0, 0, 255))
                # draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 255))
            # del draw
            # f = Path(f).resolve()
            # ff = f.parent.parent / "results" / f"{f.stem}.jpg"
            # pil_image.save(ff)
        with Storage.db.atomic():
            PhotoFace.insert_many(matched).on_conflict_ignore().execute()
        frames = []
        matched = []


@bp.cli.command("find")
@click.argument("name")
def cmd_find(name):
    res = (Photo \
           .select(Photo.full, Photo.folder, fn.STRING_AGG(Face.name, ",")) \
           .join(PhotoFace) \
           .join(Face) \
           .where(Face.name == name) \
           .group_by(Photo.full, Photo.folder))
    for rec in res.dicts().iterator():
        print(rec)


@bp.cli.command("hash")
def cmd_hash():
    res = Face.select()
    for rec in res.iterator():
        with Storage.db.atomic():
            rec.hash = Face.get_hash(pickle.loads(rec.image))
            rec.save()
        print(rec)


@bp.cli.command("dbinit")
def cmd_dbinit():
    from app.storage.models import Photo, Face, PhotoFace
    with Storage.db as db:
        db.create_tables([Photo, Face, PhotoFace])
