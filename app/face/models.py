import numpy as np
from dataclasses_json import dataclass_json
from dataclasses import dataclass
from typing import Optional


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


@dataclass_json
@dataclass
class FaceMatch:
    name: str
    face_id: int
    tagged: Optional[bytes] = None
    src: Optional[str] = None
    location: Optional[tuple[float, float, float, float]] = None
