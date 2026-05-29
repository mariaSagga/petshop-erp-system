import os
import mysql.connector
from urllib.parse import urlparse

url = urlparse(os.getenv("MYSQL_URL"))

db = mysql.connector.connect(
    host=url.hostname,
    user=url.username,
    password=url.password,
    database=url.path.replace("/", ""),
    port=url.port
)

cursor = db.cursor()
