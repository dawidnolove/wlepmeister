import platform
import socket
import uuid
import os
from pathlib import Path
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import CollectionInvalid
from pymongo.errors import ConnectionFailure, PyMongoError

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(Path(__file__).resolve().parent / ".env")
MONGO_URI = os.getenv("MONGO_URI")

CLIENT = None
DB = None
USERS_COLLECTION = None
SESSIONS_COLLECTION = None
PROJECTS_DB = None
USER_FOLDERS_COLLECTION = None
CLOUD_PROJECTS_COLLECTION = None

PROJECTS_DB_NAME = "wlepmeister_projects"
USER_FOLDERS_COLLECTION_NAME = "user"
CLOUD_PROJECTS_COLLECTION_NAME = "cloud_projects"

if not MONGO_URI:
    print("Could not connect to MongoDB: MONGO_URI env var is not set.")
else:
    try:
        CLIENT = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        CLIENT.admin.command("ping")
        DB = CLIENT["wlepmeister_db"]
        USERS_COLLECTION = DB["users"]
        SESSIONS_COLLECTION = DB["sessions"]
        PROJECTS_DB = CLIENT[PROJECTS_DB_NAME]
        if USER_FOLDERS_COLLECTION_NAME not in PROJECTS_DB.list_collection_names():
            try:
                PROJECTS_DB.create_collection(USER_FOLDERS_COLLECTION_NAME)
            except CollectionInvalid:
                pass
        USER_FOLDERS_COLLECTION = PROJECTS_DB[USER_FOLDERS_COLLECTION_NAME]
        CLOUD_PROJECTS_COLLECTION = PROJECTS_DB[CLOUD_PROJECTS_COLLECTION_NAME]
        SESSIONS_COLLECTION.create_index([("username", 1), ("login_at", -1)])
        SESSIONS_COLLECTION.create_index("session_id", unique=True)
        USER_FOLDERS_COLLECTION.create_index("username", unique=True)
        CLOUD_PROJECTS_COLLECTION.create_index(
            [("username", 1), ("project_name", 1)],
            unique=True,
        )
        CLOUD_PROJECTS_COLLECTION.create_index([("username", 1), ("updated_at", -1)])
        print("Connected to MongoDB")
    except (ConnectionFailure, PyMongoError) as exc:
        print(f"Could not connect to MongoDB: {exc.__class__.__name__}: {exc}")


def _db_ready():
    return USERS_COLLECTION is not None


def _collect_local_ips():
    ips = set()
    try:
        hostname = socket.gethostname()
        _, _, host_ips = socket.gethostbyname_ex(hostname)
        for ip in host_ips:
            if ip:
                ips.add(ip)
    except OSError:
        pass

    # This does not send traffic; OS returns local outbound interface IP.
    try:
        probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        probe.connect(("8.8.8.8", 80))
        ips.add(probe.getsockname()[0])
        probe.close()
    except OSError:
        pass

    return sorted(ips)


def _format_mac(raw_mac):
    mac_hex = f"{raw_mac:012x}"
    return ":".join(mac_hex[i : i + 2] for i in range(0, 12, 2))


def log_login_session(username):
    if SESSIONS_COLLECTION is None or not username:
        return False

    document = {
        "session_id": str(uuid.uuid4()),
        "username": username,
        "login_at": datetime.now(timezone.utc),
        "event_type": "login_success",
        "source": "desktop_app",
        "host_name": socket.gethostname(),
        "local_ips": _collect_local_ips(),
        "mac_address": _format_mac(uuid.getnode()),
        "os": platform.platform(),
        "python_version": platform.python_version(),
    }
    try:
        SESSIONS_COLLECTION.insert_one(document)
    except PyMongoError:
        return False
    return True


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
    if user is None:
        return False
    log_login_session(username)
    return True


def _cloud_ready():
    return USER_FOLDERS_COLLECTION is not None and CLOUD_PROJECTS_COLLECTION is not None


def ensure_user_project_folder(username):
    if not _cloud_ready() or not username:
        return False
    try:
        USER_FOLDERS_COLLECTION.update_one(
            {"username": username},
            {
                "$setOnInsert": {
                    "username": username,
                    "created_at": datetime.now(timezone.utc),
                },
                "$set": {"last_seen_at": datetime.now(timezone.utc)},
            },
            upsert=True,
        )
    except PyMongoError:
        return False
    return True


def save_cloud_project(username, project_name, layers_payload):
    if not _cloud_ready() or not username or not project_name:
        return False
    if not isinstance(layers_payload, list):
        return False
    if not ensure_user_project_folder(username):
        return False

    now = datetime.now(timezone.utc)
    document_update = {
        "$set": {
            "layers": layers_payload,
            "updated_at": now,
        },
        "$setOnInsert": {
            "username": username,
            "project_name": project_name,
            "created_at": now,
        },
    }
    try:
        CLOUD_PROJECTS_COLLECTION.update_one(
            {"username": username, "project_name": project_name},
            document_update,
            upsert=True,
        )
    except PyMongoError:
        return False
    return True


def list_user_cloud_projects(username):
    if not _cloud_ready() or not username:
        return []
    try:
        cursor = CLOUD_PROJECTS_COLLECTION.find(
            {"username": username},
            {"_id": 0, "project_name": 1},
        ).sort("updated_at", -1)
        return [doc["project_name"] for doc in cursor if "project_name" in doc]
    except PyMongoError:
        return []


def load_user_cloud_project(username, project_name):
    if not _cloud_ready() or not username or not project_name:
        return None
    try:
        return CLOUD_PROJECTS_COLLECTION.find_one(
            {"username": username, "project_name": project_name},
            {"_id": 0},
        )
    except PyMongoError:
        return None


def delete_user_cloud_project(username, project_name):
    if not _cloud_ready() or not username or not project_name:
        return False
    try:
        result = CLOUD_PROJECTS_COLLECTION.delete_one(
            {"username": username, "project_name": project_name}
        )
    except PyMongoError:
        return False
    return result.deleted_count > 0
