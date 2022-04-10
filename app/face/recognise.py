import face_recognition
import numpy as np
from app.face.models import MatchData, FaceMatch
from pathlib import Path
from typing import Generator
from PIL import Image, ImageDraw
from io import BytesIO


class RecogniseMeta(type):
    _instance: 'Recognise' = None
    _match_data: list[MatchData] = None

    SIZE = (1000, 1000)

    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = type.__call__(cls, *args, **kwargs)
        return cls._instance

    @property
    def match_data(cls) -> list[MatchData]:
        return cls._match_data

    def register(cls, match_data: list[MatchData]):
        cls._match_data = match_data

    def faces(cls, photo: Path, with_tags=False) -> list[FaceMatch]:
        return cls().get_face_matches(photo, with_tags)

    def batch_faces(cls, photos: list[Path], with_tags=False) -> Generator[list[FaceMatch], None, None]:
        yield from cls().get_batch_matches(photos, with_tags)


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
            draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 255))
            del draw
        output = BytesIO()
        pil_image.save(output, format="jpeg")
        for m in matches:
            m.tagged = output.getvalue()


def match_for_idx(idx) -> MatchData:
    return Recognise.match_data[idx]


class Recognise(object, metaclass=RecogniseMeta):

    def __init__(self):
        pass

    @property
    def known_face_encodings(self) -> list:
        return [x.encodings for x in Recognise.match_data]

    def get_face_matches(self, photo: Path, with_tags=False):
        if not photo.exists():
            raise FileNotFoundError
        np_img = face_recognition.load_image_file(photo.resolve().as_posix())
        img = Image.fromarray(np_img)
        img.thumbnail(Recognise.SIZE)
        np_img = np.asarray(img)
        face_locations = face_recognition.face_locations(np_img)
        face_encodings = face_recognition.face_encodings(np_img, face_locations)
        results = []
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                face_data = match_for_idx(best_match_index)
                results.append(FaceMatch(
                    name=face_data.name,
                    face_id=face_data.face_id,
                    src=photo.resolve().as_posix(),
                    location=(top, right, bottom, left)
                ))
        if with_tags:
            add_tags(results)
        return results

    def get_batch_matches(self, photos: Path, with_tags=False):
        pass
