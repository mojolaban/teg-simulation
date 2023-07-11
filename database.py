from sqlalchemy import create_engine, text
import os, random, string
from flask import jsonify
from datetime import datetime

#----0. Setting db connection
db_connection_string = os.environ['DB_CONNECTION_STRING']
engine = create_engine(db_connection_string,
                       connect_args={
                         "ssl": {
                           "ssl_ca": "/etc/ssl/cert.pem"
                         }
                       })

#----1. Assign random to treatment, start inserting initial data to db
def insert_group_treatment():
  with engine.connect() as conn:
        # Generate a random 2-character ID
        random_id = ''.join(random.choices(string.ascii_uppercase +
                                           string.ascii_lowercase + string.digits,
                                           k=2))
        # Fetch the treatment value from the log table while handling the case when num is null
        result = conn.execute(text("SELECT IFNULL((SELECT CASE WHEN num % 2 = 0 THEN 2 ELSE 1 END AS treatment FROM log ORDER BY num DESC LIMIT 1), 2) AS treatment;"))
        data = result.fetchone()
        treatment = data[0]       
        # Insert the counter, treatment, and ID values into the 'log' table
        conn.execute(text("INSERT INTO `teg-simulation`.`log` (`counter`, `gr`, `id`) VALUES ('1', :treatment, :id);"),
            {"treatment": treatment, "id": random_id})
        # Insert the treatment, ID, round, transaction, and initial asset values into the 'responses' table
        # Get the current timestamp
        current_time = datetime.now()
            # Get the current timestamp
        conn.execute(
            text("INSERT INTO `teg-simulation`.`responses`(`round`,`gr`, `id`, `trx`, `crypto`, `fiat`, `buy`, `sell`, `pos`, `t_gain`,`r_gain`,`t_tax`,`tax_disclos`,`tax_discre`,`audit`,`penalty`,`t_gain_net`,`r_gain_net`,`r_gain_final`,`r_tax`,`sec`,`price`,`crypto_prev`, `fiat_prev`)VALUES ('1', :treatment, :id, '0', '1.00', '0', '0', '0','s','0','0','0','0','0','0','0','0','0','0','0','0','0','1','0')"), {"treatment": treatment, "id": random_id})
        return str(treatment)


#----Fecth initial game data from db 
def fetch_init_data():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT round, gr, id, trx, crypto, fiat, buy, sell, pos, t_gain, r_gain, t_tax, crypto_prev, fiat_prev FROM responses ORDER BY ts DESC LIMIT 1;"))
        row = result.fetchone()
        if row:
            round_value = row[0]
            gr_value = row[1]
            id_value = row[2]
            trx_value = row[3]
            crypto_value = row[4]
            fiat_value = row[5]
            buy_value = row[6]
            sell_value = row[7]
            pos_value = row[8]
            t_gain_value = row[9]
            r_gain_value = row[10]
            t_tax_value = row[11]
            crypto_prev = row[12]
            fiat_prev = row[13]

            if gr_value == '2':
                asset_type = "Stock"
            elif gr_value == '1':
                asset_type = "Crypto"
              
            if pos_value == "s":
                pos_value = "SELL"
            elif pos_value == "b":
                pos_value = "BUY"

            init_data = {
                "round": round_value,
                "gr": gr_value,
                "id": id_value,
                "trx": trx_value,
                "crypto": crypto_value,
                "fiat": fiat_value,
                "buy": buy_value,
                "sell": sell_value,
                "pos": pos_value,
                "t_gain": t_gain_value,
                "r_gain": r_gain_value,
                "t_tax": t_tax_value,
                "asset_type": asset_type,
                "fiat_prev" : fiat_prev,
                "crypto_prev": crypto_prev
            }
            return init_data
        return None

def load_group_treatment():
  with engine.connect() as conn:
    result = conn.execute(text("select * from log"))
    print(result.all())



