import glob

import face_recognition
from flask import Flask, current_app
import os
from dataclasses_json import dataclass_json
from dataclasses import dataclass
from pathlib import Path
import pickle
import numpy as np


@dataclass_json
@dataclass
class TrainConfig:
    path: Path


@dataclass_json
@dataclass
class FaceData:
    image: np.ndarray
    encodings: list[np.ndarray]
    name: str


@dataclass_json
@dataclass
class MatchData:
    encodings: list[np.ndarray]
    name: str
    face_id: int


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
    def __cache_path(self) -> Path:
        return Path(current_app.instance_path) / "trained.dat"

    def __to_cache(self, data):
        with self.__cache_path.open("wb") as f:
            pickle.dump(data, f)
        return data

    def __from_cache(self):
        if not self.__cache_path.exists():
            return None
        with self.__cache_path.open("rb") as f:
            return pickle.load(f)

    @property
    def train_data(self) -> list[FaceData]:
        if not self.__data:
            data = self.__from_cache()
            if not data:
                self.__data = self.do_training()
            else:
                print("loaded from cache")
                self.__data = data
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
        return self.__to_cache(data)
