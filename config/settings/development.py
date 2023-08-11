from .remote import *

ALLOWED_HOSTS = [
    REMOTE_SETTINGS.PROD_URI,
    "localhost",
    "127.0.0.1",
]
CSRF_TRUSTED_ORIGINS = [
    REMOTE_SETTINGS.prod_uri_https,
]
