import face_recognition
import numpy as np
from app.face.models import MatchData, FaceMatch
from pathlib import Path
from app.storage.models import Photo
from PIL import Image, ImageDraw, ImageOps
from io import BytesIO
from multiprocessing.pool import ThreadPool
from multiprocessing import Pool
from typing import Generator


class RecogniseMeta(type):
    _match_data: list[MatchData] = None
    _instance: 'Recognise' = None

    SIZE = (300, 300)
    PAD_SIZE = (300, 300)
    POOL_SIZE = 10

    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = type.__call__(cls, *args, **kwargs)
        return cls._instance

    @property
    def known_face_encodings(cls) -> list:
        return [x.encodings for x in cls._match_data]

    def match_for_idx(cls, idx) -> MatchData:
        return cls._match_data[idx]

    def register(cls, match_data: list[MatchData]):
        cls._match_data = match_data

    def faces(
            cls,
            photo: Path,
            with_tags=False,
            tolerance=0.4
    ) -> list[FaceMatch]:
        return cls().get_face_matches(photo, with_tags, tolerance)

    def batch_faces(
            cls,
            root: Path,
            photos: list[Photo],
            with_tags=False,
            tolerance=0.4
    ) -> Generator[tuple[list[FaceMatch], Photo], None, None]:
        yield from cls().get_batch_matches(root, photos, with_tags, tolerance)


def add_tags(matches: list[FaceMatch]):
    if not len(matches):
        return
    with open(matches[0].src, "rb") as fp_img:
        pil_image = Image.open(fp_img)
        pil_image.thumbnail(Recognise.SIZE)
        for m in matches:
            draw = ImageDraw.Draw(pil_image)
            top, right, bottom, left = m.location
            name = str(m.name)
            draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255))
            text_width, text_height = draw.textsize(name)
            draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(0, 0, 255),
                           outline=(0, 0, 255))
            draw.text((left + 6, bottom - text_height - 5),
                      name, fill=(255, 255, 255, 255))
            del draw
        output = BytesIO()
        pil_image = pil_image.convert('RGB')
        pil_image.save(output, format="JPEG")
        for m in matches:
            m.tagged = output.getvalue()


def get_face_data(args):
    photo, unknown_image, face_locations, root, tolerance, with_tags = args
    photo_results = []
    face_encodings = face_recognition.face_encodings(
        unknown_image, face_locations)
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(
            Recognise.known_face_encodings, face_encoding, tolerance=tolerance)
        face_distances = face_recognition.face_distance(
            Recognise.known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            face_data = Recognise.match_for_idx(best_match_index)
            photo_results.append(FaceMatch(
                name=face_data.name,
                face_id=face_data.face_id,
                photo_id=photo.id,
                src=(root / photo.full).resolve().as_posix(),
                location=(top, right, bottom, left)
            ))
    if with_tags:
        add_tags(photo_results)
    return photo_results, photo


def get_normalized_image(args):
    root, photo = args
    f = root / photo.full
    unknown_image = face_recognition.load_image_file(
        f.resolve().as_posix()
    )
    img = Image.fromarray(unknown_image)
    img = ImageOps.pad(img, Recognise.PAD_SIZE)
    return photo, np.asarray(img)


class Recognise(object, metaclass=RecogniseMeta):

    def get_face_matches(self, photo: Path, with_tags=False, tolerance=0.4) -> list[FaceMatch]:
        if not photo.exists():
            raise FileNotFoundError
        np_img = face_recognition.load_image_file(photo.resolve().as_posix())
        img = Image.fromarray(np_img)
        img.thumbnail(Recognise.SIZE)
        np_img = np.asarray(img)
        face_locations = face_recognition.face_locations(np_img)
        face_encodings = face_recognition.face_encodings(
            np_img, face_locations)
        results = []
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(
                self.__class__.known_face_encodings, face_encoding, tolerance)
            if not matches:
                continue
            face_distances = face_recognition.face_distance(
                self.__class__.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                face_data = self.__class__.match_for_idx(best_match_index)
                results.append(FaceMatch(
                    name=face_data.name,
                    face_id=face_data.face_id,
                    src=photo.resolve().as_posix(),
                    location=(top, right, bottom, left)
                ))
        if with_tags:
            add_tags(results)
        return results

    def get_batch_matches(
            self,
            root: Path,
            photos: list[Photo],
            with_tags=False,
            tolerance=0.4,
    ) -> Generator[tuple[list[FaceMatch], Photo], None, None]:
        batch = []
        with ThreadPool(processes=self.__class__.POOL_SIZE) as n_pool:
            for photo, unknown_image in n_pool.map(get_normalized_image, [(root, p) for p in photos]):
                batch.append((photo, unknown_image))

        np_images = [x[1] for x in batch]
        batch_face_locations = face_recognition.batch_face_locations(
            np_images, number_of_times_to_upsample=1,
            batch_size=self.__class__.POOL_SIZE
        )

        with ThreadPool(processes=self.__class__.POOL_SIZE) as f_pool:
            locations = [(batch[idx][0], batch[idx][1], bl) for idx, bl in
                         enumerate(batch_face_locations)]
            args = [(photo, img, face_locations, root, tolerance, with_tags)
                    for photo, img, face_locations in locations]
            for r, p in f_pool.map(get_face_data, args):
                yield r, p
