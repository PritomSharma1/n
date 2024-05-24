from dotenv import load_dotenv
from os.path import join, dirname
import os

# load environment
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


def read_bot_token():
    TOKEN = os.environ.get("bot_token")
    return TOKEN


def read_api_id():
    API_ID = os.environ.get("api_id")
    return API_ID


def read_api_hash():
    API_HASH = os.environ.get("api_hash")
    return API_HASH
