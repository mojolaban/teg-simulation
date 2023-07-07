from sqlalchemy import create_engine, text
import os
from flask import jsonify

db_connection_string = os.environ['DB_CONNECTION_STRING']

engine = create_engine(db_connection_string,
                       connect_args={
                         "ssl": {
                           "ssl_ca": "/etc/ssl/cert.pem"
                         }
                       })

def insert_group_treatment():
  with engine.connect() as conn:
    conn.execute(text("INSERT INTO `teg-simulation`.`log` (`counter`) VALUES ('1');"))
    result = conn.execute(text("SELECT CASE WHEN access_num % 2 = 0 THEN 2 ELSE 1 END AS treatment FROM log ORDER BY access_num DESC LIMIT 1;"))
    data = result.fetchone()
    treatment = data[0] if data else None
    return str(treatment)

def load_group_treatment():
  with engine.connect() as conn:
    result = conn.execute(text("select * from log"))
    print(result.all())


from datetime import datetime
print(type(datetime.now()))