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


#----0.1 Assign treatment based on language selection
def insert_group_lang(lang):
  with engine.connect() as conn:
    # Generate a random 2-character ID
    random_id = ''.join(random.choices(string.ascii_uppercase +
                                       string.ascii_lowercase + string.digits,
                                       k=2))
    # Fetch the treatment value from the log table while handling the case when num is null
    result = conn.execute(text("SELECT IFNULL((SELECT CASE WHEN num % 2 = 0 THEN 2 ELSE 1 END AS treatment FROM log ORDER BY num DESC LIMIT 1), 2) AS treatment;"))
    data = result.fetchone()
    treatment = data[0]
    # Map language to the corresponding value
    lang_value = 1 if lang == 'Indonesian' else 0
    # Insert the counter, treatment, ID, and language values into the 'log' table
    conn.execute(text("INSERT INTO `teg-simulation`.`log` (`counter`, `gr`, `id`,`lang` ) VALUES ('1', :treatment, :id, :lang);"),
                 {"treatment": treatment, "id": random_id, "lang": lang_value})
    # Create a dictionary with the treatment, id, and lang values
    treatment_dict = {"treatment": treatment, "id": random_id, "lang": lang_value}

  return treatment_dict


#----1. Assign random to treatment, start inserting initial data to db
def insert_group_treatment(gr,id):
  with engine.connect() as conn:
        # Insert the treatment, ID, round, transaction, initial asset, and other values into the 'responses' table
        conn.execute(
            text("INSERT INTO `teg-simulation`.`responses`(`round`,`gr`, `id`, `trx`, `crypto`, `fiat`, `buy`, `sell`, `pos`, `t_gain`, `r_gain`, `t_tax`, `tax_disclos`, `audit`, `t_gain_net`, `r_gain_net`,`r_tax`,`sec`,`price`,`crypto_prev`, `fiat_prev`, `buy_prev`, `r_gain_prev`,`r_tax_prev`)VALUES ('0', :gr, :id, '0', '1.00', '0', '0', '0','s','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0')"), {"gr": gr, "id": id})


#----1a. Insert participant profile
def insert_demog(gender, age, education_level, current_education, country_residence, citizenship, asset_experience, tax_experience, description,id):
  with engine.connect() as conn:
      conn.execute(
          text("INSERT INTO `teg-simulation`.`demog`(`gender`, `age`, `education_level`, `current_education`, `country_residence`, `citizenship`, `asset_experience`, `tax_experience`, `description`, `id`) VALUES (:gender, :age, :education_level, :current_education, :country_residence, :citizenship, :asset_experience, :tax_experience, :description, :id);"), 
          {"gender": gender, "age": age, "education_level": education_level, "current_education": current_education, "country_residence": country_residence, "citizenship": citizenship, "asset_experience": asset_experience, "tax_experience": tax_experience, "description": description, "id": id}
      )


#----2. Fecth initial game data from db 
def fetch_init_data(id):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT round, gr, id, trx, crypto, fiat, buy, sell, pos, t_gain, r_gain, t_tax, crypto_prev, fiat_prev, buy_prev, r_tax, r_gain_net, t_gain_net, r_gain_prev, r_tax_prev, tax_disclos, tax_discre, audit, penalty, r_gain_final FROM responses WHERE id = :id ORDER BY ts DESC LIMIT 1;"), {"id": id})
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
            buy_prev = row[14]
            r_tax = row[15]
            r_gain_net = row[16]
            t_gain_net = row[17]
            r_gain_prev = row[18]
            r_tax_prev = row[19]
            tax_disclos = row[20]
            tax_discre = row[21]
            audit = row[22]
            penalty = row[23]
            r_gain_final = row[24]

            if gr_value == '2':
                asset_type = "Crypto"
            elif gr_value == '1':
                asset_type = "Stock"
              
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
                "crypto_prev": crypto_prev,
                "buy_prev": buy_prev,
                "r_tax": r_tax,
                "r_gain_net":r_gain_net,
                "t_gain_net":t_gain_net,
                "r_gain_prev":r_gain_prev,
                "r_tax_prev":r_tax_prev,
                "tax_disclos":tax_disclos,
                "tax_discre":tax_discre,
                "audit":audit,
                "penalty":penalty,
                "r_gain_final":r_gain_final
            }
            return init_data
        return None
      

#----3. Retrieve data from db 
def retrieve_data(id):
    user_id = id.replace('\n', '').strip()

    with engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT round, gr, id, trx, crypto, fiat, buy, sell, pos, t_gain, r_gain, t_tax, crypto_prev, fiat_prev, buy_prev, r_tax, r_gain_net, t_gain_net, r_gain_prev, r_tax_prev, tax_disclos, tax_discre, audit, penalty, r_gain_final, sec, price  FROM responses WHERE id = :id ORDER BY ts DESC LIMIT 1;"),
            {"id": user_id})
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
            buy_prev = row[14]
            r_tax = row[15]
            r_gain_net = row[16]
            t_gain_net = row[17]
            r_gain_prev = row[18]
            r_tax_prev = row[19]
            tax_disclos = row[20]
            tax_discre = row[21]
            audit = row[22]
            penalty = row[23]
            r_gain_final = row[24]
            sec_value = row[25]
            price_value = row[26]

            if gr_value == '2':
                asset_type = "Crypto"
            elif gr_value == '1':
                asset_type = "Stock"

            if pos_value == "s":
                pos_value = "SELL"
            elif pos_value == "b":
                pos_value = "BUY"

            updated_data = {
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
                "fiat_prev": fiat_prev,
                "crypto_prev": crypto_prev,
                "buy_prev": buy_prev,
                "r_tax": r_tax,
                "r_gain_net": r_gain_net,
                "t_gain_net": t_gain_net,
                "r_gain_prev": r_gain_prev,
                "r_tax_prev": r_tax_prev,
                "tax_disclos": tax_disclos,
                "tax_discre": tax_discre,
                "audit": audit,
                "penalty": penalty,
                "r_gain_final": r_gain_final,
                "sec" : sec_value,
                "price": price_value
            }
          

            return jsonify(updated_data)

    return jsonify({})

#---4. Send data to db:
def send_data(data):
    user_id = data.replace('\n', '').strip()

    with engine.connect() as conn:
        # Insert the treatment, ID, round, transaction, initial asset, and other values into the 'responses' table
        conn.execute(
            text("INSERT INTO `teg-simulation`.`responses`(`round`,`gr`, `id`, `trx`, `crypto`, `fiat`, `buy`, `sell`, `pos`, `t_gain`,`r_gain`,`t_tax`,`tax_disclos`,`audit`,`t_gain_net`,`r_gain_net`,`r_tax`,`sec`,`price`,`crypto_prev`, `fiat_prev`,`buy_prev`,`r_gain_prev`, `r_tax_prev`)VALUES ('1', :treatment, :id, '0', '1.00', '0', '0', '0','s','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0')"), {"treatment": treatment, "id": random_id})
      # Create a dictionary with the treatment and id values
        treatment = {"treatment": treatment, "id": random_id}
        return treatment





def fetch_update_data(id):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT round, gr, id, trx, crypto, fiat, buy, sell, pos, t_gain, r_gain, t_tax, crypto_prev, fiat_prev, buy_prev, r_tax, r_gain_net, t_gain_net, r_gain_prev, r_tax_prev, tax_disclos, tax_discre, audit, penalty, r_gain_final FROM responses WHERE id = :id ORDER BY ts DESC LIMIT 1;"), {"id": id})
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
            buy_prev = row[14]
            r_tax = row[15]
            r_gain_net = row[16]
            t_gain_net = row[17]
            r_gain_prev = row[18]
            r_tax_prev = row[19]
            tax_disclos = row[20]
            tax_discre = row[21]
            audit = row[22]
            penalty = row[23]
            r_gain_final = row[24]

            if gr_value == '2':
                asset_type = "Crypto"
            elif gr_value == '1':
                asset_type = "Stock"
              
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
                "crypto_prev": crypto_prev,
                "buy_prev": buy_prev,
                "r_tax": r_tax,
                "r_gain_net":r_gain_net,
                "t_gain_net":t_gain_net,
                "r_gain_prev":r_gain_prev,
                "r_tax_prev":r_tax_prev,
                "tax_disclos":tax_disclos,
                "tax_discre":tax_discre,
                "audit":audit,
                "penalty":penalty,
                "r_gain_final":r_gain_final
            }
            return update_data
        return None


def load_group_treatment():
  with engine.connect() as conn:
    result = conn.execute(text("select * from log"))
    print(result.all())



