from io import BytesIO
from PIL import Image
from app.face.models import FaceMatch
import cv2
import numpy as np
from pathlib import Path


def show_tagged(matches: list[FaceMatch], wait=10):
    buff = BytesIO(matches[0].tagged)
    buff.seek(0)
    image = Image.open(buff)
    img = np.asarray(image)
    window_name = ", ".join([x.name for x in matches])
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    cv2.imshow(window_name, img)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
    cv2.waitKey(wait * 1000)
    cv2.destroyAllWindows()


def save_tagged(matches: list[FaceMatch], dst: Path):
    buff = BytesIO(matches[0].tagged)
    buff.seek(0)
    image = Image.open(buff)
    f_name = Path(matches[0].src).name
    if not dst.exists():
        dst.mkdir(parents=True)
    out_path = dst / f_name
    image.save(out_path.as_posix(), "jpeg")
