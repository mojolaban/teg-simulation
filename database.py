from sqlalchemy import create_engine, text

db_connection_string = "mysql+pymysql://sq8bvsyd7fysrl9uaiao:pscale_pw_FipM9Tn6F6p5Mghz2BhDgt7dZ38JSJeXvcb6BmIZe4Q@aws.connect.psdb.cloud/teg-simulation?charset=utf8mb4"

engine = create_engine(db_connection_string,
                       connect_args={
                         "ssl": {
                           "ssl_ca": "/etc/ssl/cert.pem"
                         }
                       })

with engine.connect() as conn:
  result = conn.execute(text("select*from responses"))
  print(result.all())
  