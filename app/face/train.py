import glob
import face_recognition
from flask import Flask, current_app
import os
from dataclasses_json import dataclass_json
from dataclasses import dataclass
from pathlib import Path
from app.face.models import FaceData


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
    def train(cls) -> list[FaceData]:
        return cls().do_training()

    @property
    def data(cls) -> list[FaceData]:
        return cls().train_data


class Train(object, metaclass=TrainMeta):
    __data = None

    def __person_images(self):
        for root, dirs, files in os.walk(self.config.path.as_posix()):
            for d in filter(lambda x: x not in [".", ".."], dirs):
                yield d, glob.glob(f"{root}/{d}/**.jpg")

    @property
    def train_data(self) -> list[FaceData]:
        if not self.__data:
            self.__data = self.do_training()
        return self.__data

    def do_training(self) -> list[FaceData]:
        data = []
        for person, photos in self.__person_images():
            for photo in photos:
                face = face_recognition.load_image_file(photo)
                face_bounding_boxes = face_recognition.face_locations(face)
                if len(face_bounding_boxes) == 1:
                    face_enc = face_recognition.face_encodings(face)[0]
                    data.append(FaceData(name=person, image=face, encodings=face_enc))
        return data
