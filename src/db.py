import zlib
from datetime import datetime, timezone

from bson.binary import Binary
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError

MONGO_URI = "mongodb+srv://wlepyuser:BazaDanych1.@wlepmaister.5hikzgm.mongodb.net/?appName=WlepMaister"

CLIENT = None
DB = None
USERS_COLLECTION = None
PROJECTS_COLLECTION = None

try:
    CLIENT = MongoClient(MONGO_URI)
    CLIENT.admin.command("ping")
    DB = CLIENT["wlepmeister_db"]
    USERS_COLLECTION = DB["users"]
    PROJECTS_COLLECTION = DB["projects"]
    PROJECTS_COLLECTION.create_index([("username", 1), ("created_at", -1)])
    print("✅ Połączono z MongoDB")
except ConnectionFailure:
    print("❌ Nie udało się połączyć z MongoDB")


def _db_ready():
    return USERS_COLLECTION is not None


def user_exists(username):
    if not _db_ready() or not username:
        return False
    return USERS_COLLECTION.find_one({"username": username}, {"_id": 1}) is not None


def create_user(username, password):
    if not _db_ready():
        return False
    if user_exists(username):
        return False
    USERS_COLLECTION.insert_one({"username": username, "password": password})
    return True


def login_user(username, password):
    if not _db_ready():
        return False
    user = USERS_COLLECTION.find_one({"username": username, "password": password})
    return user is not None


def _encode_png_payload(png_bytes):
    compressed = zlib.compress(png_bytes, level=9)
    if len(compressed) < len(png_bytes):
        return Binary(compressed), "zlib+png"
    return Binary(png_bytes), "png"


def save_user_png_export(username, file_name, png_bytes, image_size):
    if PROJECTS_COLLECTION is None or not username or not png_bytes:
        return False

    payload, encoding = _encode_png_payload(png_bytes)
    width, height = image_size
    project_document = {
        "username": username,
        "project_type": "png_export",
        "file_name": file_name,
        "content_type": "image/png",
        "encoding": encoding,
        "png_blob": payload,
        "byte_size": len(png_bytes),
        "stored_byte_size": len(payload),
        "width": int(width),
        "height": int(height),
        "created_at": datetime.now(timezone.utc),
    }
    try:
        PROJECTS_COLLECTION.insert_one(project_document)
    except PyMongoError:
        return False
    return True
