import glob
import face_recognition
import numpy as np
from flask import Flask, current_app
from tqdm import tqdm
from dataclasses_json import dataclass_json
from dataclasses import dataclass
from pathlib import Path
from app.face.models import FaceData
from typing import Generator
from PIL import Image, ImageOps


@dataclass_json
@dataclass
class TrainConfig:
    path: Path


class TrainMeta(type):
    config: TrainConfig = None
    _instance: 'Train' = None

    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = type.__call__(cls, *args, **kwargs)
        return cls._instance

    def register(cls, app: 'Flask'):
        cls.config = TrainConfig.from_dict(app.config.get_namespace("FACE_"))
        cls.config.path = Path(app.instance_path) / cls.config.path

    @property
    def train(cls) -> Generator[FaceData, None, None]:
        yield from cls().do_training()

    @property
    def data(cls) -> list[FaceData]:
        return cls().train_data


class Train(object, metaclass=TrainMeta):
    __data = None

    def __person_images(self):
        root = self.config.path.absolute()
        for f in tqdm(glob.glob(f"{root.as_posix()}/**/**.jpg", recursive=True)):
            fp = Path(f).absolute()
            fr = fp.relative_to(root)
            yield fr.parent.name, f

    @property
    def train_data(self) -> list[FaceData]:
        if not self.__data:
            self.__data = self.do_training()
        return self.__data

    def do_training(self) -> list[FaceData]:
        for person, photo in self.__person_images():
            face = face_recognition.load_image_file(photo)
            img = Image.fromarray(face)
            padded = ImageOps.pad(img, (500, 500))
            face = np.asarray(padded)
            face_bounding_boxes = face_recognition.face_locations(face, model='cnn')
            if not len(face_bounding_boxes):
                face_bounding_boxes = face_recognition.face_locations(face, number_of_times_to_upsample=3, model='cnn')
            if len(face_bounding_boxes) == 1:
                face_enc = face_recognition.face_encodings(face)
                if not len(face_enc):
                    face_enc = face_recognition.face_encodings(face, num_jitters=5, model='large')
                if face_enc:
                    yield FaceData(name=person, image=face, encodings=face_enc[0])
                else:
                    p = Path(photo)
                    p.rename(f"{p}_NO-ENCODINGS")
            else:
                p = Path(photo)
                p.rename(f"{p}_FACES_FOUND_{len(face_bounding_boxes)}")
