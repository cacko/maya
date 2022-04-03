from pathlib import Path
from sync.s3 import S3, S3Upload
from sync.firestore import Firestore
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from sync import log
from enum import Enum


class Method(Enum):
    UPLOAD = "upload"
    THUMB = "upload_thumbs"


def upload(item: S3Upload, progress: tqdm):
    src, full, thumb = S3.upload(item)
    Firestore.store(src, full, thumb)
    progress.update(1)
    return src, full, thumb


def upload_thumbs(item: S3Upload, progress: tqdm):
    src, full, thumb = S3.thumb(item)
    progress.update(1)
    return src, full, thumb


class Uploader:
    queue: list[S3Upload] = None
    isRunning = False
    executor: ThreadPoolExecutor = None
    POOL_SIZE = 10
    progress: tqdm = None
    processed = []
    tracking = None
    method: Method = None

    def __init__(self, total, method: Method = Method.UPLOAD):
        self.method = method
        self.queue = []
        self.progress = tqdm(total=total)

        if self.method == Method.THUMB:
            tf = Path("processed_thumbs")
        else:
            tf = Path("processed")

        if tf.exists():
            self.processed = list(map(lambda x: x.strip(), tf.read_text().split("\n")))
        self.tracking = tf.open("a")

    def add(self, src: str, dst: str):
        if src in self.processed:
            return self.progress.update()
        self.queue.append(S3Upload(src=src, dst=dst))
        self.run()

    def _job(self, executor):
        items = []
        while len(self.queue):
            items.append(self.queue.pop(0))
            if len(items) == self.POOL_SIZE:
                break
        if self.method == Method.THUMB:
            return map(lambda item: executor.submit(upload_thumbs, item, self.progress), items)
        else:
            return map(lambda item: executor.submit(upload, item, self.progress), items)

    def run(self):
        if self.isRunning:
            return
        self.isRunning = True
        with ThreadPoolExecutor(max_workers=self.POOL_SIZE) as executor:
            for future in as_completed(self._job(executor)):
                try:
                    src, full, thumb = future.result()
                    self.tracking.write(f"{src}\n")
                except Exception as e:
                    log.error(e, exc_info=True)
            self.isRunning = False

    def __del__(self):
        self.tracking.close()
