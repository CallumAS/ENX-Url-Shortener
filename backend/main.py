from fastapi import FastAPI
import psycopg
from aiohcaptcha import HCaptchaClient
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
import re
import os
from dotenv import load_dotenv

load_dotenv()
host = os.getenv('host')
port = os.getenv('port')
dbname = os.getenv('dbname')
user = os.getenv('user')
password = os.getenv('password')
table = os.getenv('table')
hcaptcha = os.getenv('hcaptcha')


# sql queries
def create_table():
    with psycopg.connect("host='{}' port='{}' dbname='{}' user='{}' password='{}'".format(host, port, dbname, user,
                                                                                          password)) as conn:
        # Open a cursor to perform database operations
        with conn.cursor() as cur:
            # Execute a command: this creates a new table
            cur.execute("""
                CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
                CREATE TABLE IF NOT EXISTS """ + table + """ (
                    id text DEFAULT substring(uuid_generate_v4()::text, 1, 8) PRIMARY KEY,
                    link text
                )
            """)


def add_link(link):
    with psycopg.connect("host='{}' port='{}' dbname='{}' user='{}' password='{}'".format(host, port, dbname, user,
                                                                                          password)) as conn:
        # Open a cursor to perform database operations
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO " + table + " (link) VALUES (%s) RETURNING id",
                (link,)
            )
            inserted_id = cur.fetchone()[0]
            conn.commit()
            return inserted_id


def find_link(code):
    with psycopg.connect("host='{}' port='{}' dbname='{}' user='{}' password='{}'".format(host, port, dbname, user,
                                                                                          password)) as conn:
        # Open a cursor to perform database operations
        with conn.cursor() as cur:
            cur.execute("SELECT link FROM " + table + " WHERE id = (%s) LIMIT 1", (code,))
            return cur.fetchone()[0]


# create tables if not exist
create_table()


# Post Data for shortening link
class ShortenData(BaseModel):
    link: str
    token: str


# url validator
def is_valid_url(url):
    pattern = re.compile(
        r'^(https?://)?'  # protocol
        r'(www\.)?'  # optional 'www' subdomain
        r'[a-zA-Z0-9.-]+'  # domain name
        r'\.[a-zA-Z]{2,}'  # top-level domain (e.g., .com, .net)
        r'(/[^\s]*)?'  # optional path
        r'$'  # end of string
    )
    return bool(re.match(pattern, url))


# HTTP SERVER
app = FastAPI()


@app.post("/shorten")
async def shorten(data: ShortenData):
    if not is_valid_url(data.link):
        return {"status": False, "message": "invalid URL"}

    try:
        client = HCaptchaClient(hcaptcha)
        is_valid = await client.verify(data.token)  # a boolean
        if is_valid:
            return {"status": True, "link": data.link, "shortened": add_link(data.link)}
        else:
            return {"status": False, "message": "invalid captcha"}

    except:
        return {"status": False, "message": "captcha error"}


@app.get("/l/{link_id}")
async def getlink(link_id: str):
    response = RedirectResponse(url=find_link(link_id))
    return response


app.mount("/", StaticFiles(directory="static", html=True), name="static")
