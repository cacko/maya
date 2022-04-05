from pathlib import Path
from app.s3 import S3, S3Upload
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum
from flask import current_app
from typing import Callable


class Method(Enum):
    UPLOAD = "upload"
    THUMB = "upload_thumbs"


def upload(item: S3Upload, progress: tqdm):
    folder, src, full, thumb = S3.upload(item)
    progress.update(1)
    return folder, src, full, thumb


def upload_thumbs(item: S3Upload, progress: tqdm):
    folder, src, full, thumb = S3.thumb(item)
    progress.update(1)
    return folder, src, full, thumb


class Uploader:
    queue: list[S3Upload] = None
    isRunning = False
    executor: ThreadPoolExecutor = None
    POOL_SIZE = 10
    progress: tqdm = None
    processed = []
    tracking = None
    method: Method = None
    callback: Callable = None

    def __init__(self, total, method: Method = Method.UPLOAD, callback: Callable = None):
        self.method = method
        self.queue = []
        self.progress = tqdm(total=total)
        self.callback = callback

        if self.method == Method.THUMB:
            tf = Path("processed_thumbs")
        else:
            tf = Path("processed")

        if tf.exists():
            self.processed = list(map(lambda x: x.strip(), tf.read_text().split("\n")))
        self.tracking = tf.open("a")

    def add(self, src: str, dst: str, skip_upload=False):
        skip_upload = any([skip_upload, src in self.processed])
        self.queue.append(S3Upload(src=src, dst=dst, skip_upload=skip_upload))
        self.run()

    def _job(self, executor):
        items = []
        while len(self.queue):
            items.append(self.queue.pop(0))
            if len(items) == self.POOL_SIZE:
                break
        if not len(items):
            return None
        if self.method == Method.THUMB:
            return map(lambda item: executor.submit(upload_thumbs, item, self.progress), items)
        else:
            return map(lambda item: executor.submit(upload, item, self.progress), items)

    def run(self):
        if self.isRunning:
            return
        self.isRunning = True
        with ThreadPoolExecutor(max_workers=self.POOL_SIZE) as executor:
            tasks = self._job(executor)
            if not tasks:
                return
            for future in as_completed(tasks):
                try:
                    folder, src, full, thumb = future.result()
                    if src not in self.processed:
                        self.tracking.write(f"{src}\n")
                    if self.callback is not None:
                        self.callback(folder, src, full, thumb)
                except Exception as e:
                    current_app.logger.error(e, exc_info=True)
            self.isRunning = False

    def __del__(self):
        self.tracking.close()
