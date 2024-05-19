import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
UPPER_DIR = os.path.abspath(os.path.join(ROOT_DIR, '..'))


APK_JSON_PATH = os.getenv("APK_JSON_PATH", "test/apks.json")
APK_DIR = os.getenv("APK_DIR", os.path.join(UPPER_DIR, "test/test-apks"))
RES_DIR = os.getenv("RES_DIR", "test/test-res")

REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)

RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", 5672)

TMP_PATH = "/tmp"
APKEDITOR_PATH = "/APKEditor.jar"