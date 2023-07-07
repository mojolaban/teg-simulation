from sqlalchemy import create_engine, text
import os

db_connection_string = os.environ['DB_CONNECTION_STRING']

engine = create_engine(db_connection_string,
                       connect_args={
                         "ssl": {
                           "ssl_ca": "/etc/ssl/cert.pem"
                         }
                       })

def load_group_treatment():
  with engine.connect() as conn:
    result = conn.execute(text("select from log"))
    print(result.all())

from datetime import datetime
print(type(datetime.now()))