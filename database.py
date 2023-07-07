from sqlalchemy import create_engine, text
import os, random, string
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
        # Generate a random 5-character ID
        random_id = ''.join(random.choices(string.ascii_uppercase +
                                           string.ascii_lowercase + string.digits,
                                           k=3))
        # Fetch the treatment value from the log table,
        #handling the case when access_num is 1
        result = conn.execute(text
                              ("SELECT IFNULL((SELECT CASE WHEN access_num % 2 = 0 THEN 2 ELSE 1 END AS treatment FROM log ORDER BY access_num DESC LIMIT 1), 2) AS treatment;"))
        data = result.fetchone()
        treatment = data[0]       
        # Insert the counter, treatment, and ID values into the 'log' table
        conn.execute(
            text("INSERT INTO `teg-simulation`.`log` (`counter`, `gr`, `id`) VALUES ('1', :treatment, :id);"),
            {"treatment": treatment, "id": random_id}
        )
        return str(treatment)
    

def insert_game_data():
  with engine.connect() as conn:
    conn.execute(text("INSERT INTO `teg-simulation`.`log` (`counter`) VALUES ('1');"))


def load_group_treatment():
  with engine.connect() as conn:
    result = conn.execute(text("select * from log"))
    print(result.all())


from datetime import datetime
print(type(datetime.now()))