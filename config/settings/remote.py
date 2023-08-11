# flake8: noqa
from .base import *

from .extension import RemoteSettings

REMOTE_SETTINGS = RemoteSettings()
locals().update(REMOTE_SETTINGS.dict(exclude_none=True))

MIDDLEWARE.append("whitenoise.middleware.WhiteNoiseMiddleware")
