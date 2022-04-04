from sync.config import Config
from exif import Image
from google.cloud.firestore import Client, WriteBatch
from dataclasses_json import dataclass_json
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timezone
from hashlib import blake2s


@dataclass_json
@dataclass
class PhotoDocument:
    full: str
    thumb: str
    folder: str
    info: dict
    timestamp: str


@dataclass_json
@dataclass
class FirebaseConfig:
    admin_json: str


class FirestoreMeta(type):
    _instance: 'Firestore' = None


    def __call__(cls, *args, **kwds):
        if not cls._instance:
            cls._instance = type.__call__(cls, *args, **kwds)
        return cls._instance

    def store(cls, src, full, thumb):
        cls().store_document(src, full, thumb)


class Firestore(object, metaclass=FirestoreMeta):
    __client: Client = None
    __config: FirebaseConfig = None
    __batch: WriteBatch = None
    MAX_BATCH_SIZE = 50

    def __init__(self) -> None:
        config: FirebaseConfig = FirebaseConfig.from_dict(
            Config.namespace("FIREBASE_"))
        self.__client = Client.from_service_account_json(
            config.admin_json
        )
        self.__config = config

    @property
    def batch(self):
        if not self.__batch:
            self.__batch = WriteBatch(client=self.__client)
        if len(self.__batch) >= self.MAX_BATCH_SIZE:
            self.__batch.commit()
        return self.__batch


    def store_document(self, src, full, thumb):
        doc_id = blake2s(digest_size=20)
        doc_id.update(full.encode())
        doc_ref = self.__client.collection('photos').document(doc_id.hexdigest())
        document = PhotoDocument(
            full=full,
            thumb=thumb,
            folder=Path(full).parent.stem,
            info=Firestore.get_exif(src),
            timestamp=Firestore.get_timestamp(src).isoformat()
        )
        self.batch.set(doc_ref, document.to_dict())

    def __del__(self):
        if len(self.batch):
            self.batch.commit()
