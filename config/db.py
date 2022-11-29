import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.sql import text

load_dotenv()
username = os.getenv('USERNAME')
path = os.getenv('HOST')
password = os.getenv('PASSWORD')
port = os.getenv('PORT')
db_name = os.getenv('DB')

db_string = f"postgresql://{username}:{password}@{path}:{port}/{db_name}"
db = create_engine(db_string)
conn = db.connect()

def con():
    return conn

def listresult(result):
    res = {}
    l = []

    for p in result:
        res.update(p)        
        l.append(tuple(p))
    keys = res.keys()
    output_data = [{i:j for i,j in zip(keys,k)} for k in l] 

    return output_data


