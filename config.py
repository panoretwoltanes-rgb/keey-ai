import os
BASE = os.path.dirname(os.path.abspath(__file__))
APP_NAME = "KEEY AI 报价系统"
VERSION = "1.0.0"
HOST = "127.0.0.1"
PORT = 5000
DEBUG = True
SECRET_KEY = "dev"
OUTPUT_DIR = os.path.join(BASE, "output")
LOG_DIR = os.path.join(BASE, "logs")
UPLOAD_DIR = os.path.join(BASE, "uploads")
TEMP_DIR = os.path.join(BASE, "temp")