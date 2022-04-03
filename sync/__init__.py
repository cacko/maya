__name__ = "photosync"
__version__ = "0.1.0"


import logging
from os import environ
import warnings

warnings.filterwarnings("ignore")

logging.basicConfig(
    level=getattr(logging, environ.get("photosync", "INFO")),
    format="%(filename)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("photosync")
