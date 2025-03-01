from sqlalchemy import create_engine, text
import os, random, string
from flask import jsonify
from datetime import datetime

#----0. Setting db connection
db_connection_string = os.environ['DB_CONNECTION_STRING']
engine = create_engine(db_connection_string)
#engine = create_engine(db_connection_string,
#                       connect_args={
#                         "ssl": {
#                           "ssl_ca": "/etc/ssl/cert.pem"
#                         }
#                       })


#----0.1 Assign treatment based on language selection
def insert_group_lang(lang):
    with engine.connect() as conn:
        while True:
            # Generate a random 2-character ID
            random_id = ''.join(random.choices(string.ascii_uppercase +
                                               string.ascii_lowercase + string.digits,
                                               k=2))

            # Check if the generated ID already exists in the database
            existing_id_result = conn.execute(text("""
                SELECT `id`
                FROM `log`
                WHERE `id` = :random_id
            """), {'random_id': random_id})
            existing_id = existing_id_result.fetchone()

            # If the ID does not exist, break the loop
            if not existing_id:
                break

        # Convert lang to the expected format for comparison
        lang_value = 1 if lang == 'Indonesian' else 0

        # Attempt to fetch the last entry's treatment for the given lang
        last_entry_for_lang_result = conn.execute(text("""
            SELECT `gr`, `lang`
            FROM `log`
            WHERE `lang` = :lang
            ORDER BY `num` DESC
            LIMIT 1
        """), {'lang': lang_value})
        last_entry_data = last_entry_for_lang_result.fetchone()

        # Determine treatment based on the last entry for the given lang
        if last_entry_data:
            last_treatment, _ = last_entry_data
            # Toggle the treatment based on the last entry for the given lang
            treatment = '2' if last_treatment == '1' else '1'
        else:
            # Default treatment if there's no previous entry for the given lang
            treatment = '1'

        # Now, fetch the last entry with the same treatment to determine 'au' value
        last_entry_for_treatment_result = conn.execute(text("""
            SELECT `au`
            FROM `log`
            WHERE `gr` = :treatment
            ORDER BY `num` DESC
            LIMIT 1
        """), {'treatment': treatment})
        last_au_data = last_entry_for_treatment_result.fetchone()

        # Determine the 'au' value to alternate (0 or 1)
        if last_au_data:
            last_au = last_au_data[0]
            # Toggle 'au' value based on the last entry's 'au'
            au_value = 1 if last_au == 0 else 0
        else:
            # Default 'au' if there's no previous entry for the treatment
            au_value = 0

        # Insert the new record with the determined treatment and 'au'
        conn.execute(text("""
            INSERT INTO `log` (`counter`, `gr`, `id`, `lang`, `au`)
            VALUES ('1', :treatment, :id, :lang, :au);
        """), {"treatment": treatment, "id": random_id, "lang": lang_value, "au": au_value})

        # Create and return a dictionary with the treatment, id, lang, and au values
        treatment_dict = {"treatment": treatment, "id": random_id, "lang": lang_value, "au": au_value}

    return treatment_dict

  


#----1. Assign random to treatment, start inserting initial data to db
def insert_group_treatment(gr,id,lang):
  with engine.connect() as conn:
        # Insert the treatment, ID, round, transaction, initial asset, and other values into the 'responses' table
        conn.execute(
            text("INSERT INTO `teg-simulation-sandbox`.`responses`(`round`,`gr`, `id`, `lang`, `trx`, `crypto`, `fiat`, `buy`, `sell`, `pos`, `t_gain`, `r_gain`, `t_tax`, `tax_disclos`, `audit`, `t_gain_net`, `r_gain_net`,`r_tax`,`sec`,`price`,`crypto_prev`, `fiat_prev`, `buy_prev`, `r_gain_prev`,`r_tax_prev`)VALUES ('0', :gr, :id, :lang, '0', '1.00', '0', '0', '0','s','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0')"), {"gr": gr, "id": id, "lang": lang})


#----1a. Insert participant profile
def insert_demog(gender, age, education_level, current_education, country_residence, citizenship, asset_experience, tax_experience, description,id):
  with engine.connect() as conn:
      conn.execute(
          text("INSERT INTO `teg-simulation-sandbox`.`demog`(`gender`, `age`, `education_level`, `current_education`, `country_residence`, `citizenship`, `asset_experience`, `tax_experience`, `description`, `id`) VALUES (:gender, :age, :education_level, :current_education, :country_residence, :citizenship, :asset_experience, :tax_experience, :description, :id);"), 
          {"gender": gender, "age": age, "education_level": education_level, "current_education": current_education, "country_residence": country_residence, "citizenship": citizenship, "asset_experience": asset_experience, "tax_experience": tax_experience, "description": description, "id": id}
      )


#----2. Fecth initial game data from db 
def fetch_init_data(id):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT round, gr, id, trx, crypto, fiat, buy, sell, pos, t_gain, r_gain, t_tax, crypto_prev, fiat_prev, buy_prev, r_tax, r_gain_net, t_gain_net, r_gain_prev, r_tax_prev, tax_disclos, tax_discre, audit, penalty, r_gain_final, lang FROM responses WHERE id = :id ORDER BY ts DESC LIMIT 1;"), {"id": id})
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
            lang = row[25]
 
            asset_type = None 
            if gr_value == '2' and lang==0:
                asset_type = "Crypto"
            elif gr_value == '2' and lang==1:
                asset_type = "Kripto"
            elif gr_value == '1' and lang==0:
                asset_type = "Stock"
            elif gr_value == '1' and lang==1:
                asset_type = "Saham"
              
            if pos_value == "s" and lang==0:
                pos_value = "SELL"
            elif pos_value == "s" and lang==1:
                pos_value = "JUAL"
            elif pos_value == "b" and lang==0:
                pos_value = "BUY"
            elif pos_value == "b" and lang==1:
                pos_value = "BELI"
            # Format crypto value for Indonesian number formatting
            if lang == 1:  # Indonesian
                crypto_value = "{:,.2f}".format(row[4]).replace(",", "X").replace(".", ",").replace("X", ".")
            else:
                crypto_value = str(row[4])
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
                "r_gain_final":r_gain_final,
                "lang": lang
            }
            return init_data
        return None
      

#----3. Retrieve data from db 
def retrieve_data(id):
    user_id = id.replace('\n', '').strip()

    with engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT round, gr, id, trx, crypto, fiat, buy, sell, pos, t_gain, r_gain, t_tax, crypto_prev, fiat_prev, buy_prev, r_tax, r_gain_net, t_gain_net, r_gain_prev, r_tax_prev, tax_disclos, tax_discre, audit, penalty, r_gain_final, sec, price, lang  FROM responses WHERE id = :id ORDER BY ts DESC LIMIT 1;"),
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
            lang = row[27]
          
            asset_type = None
            if gr_value == '2' and lang==0:
                asset_type = "Crypto"
            elif gr_value == '2' and lang==1:
                asset_type = "Kripto"
            elif gr_value == '1' and lang==0:
                asset_type = "Stock"
            elif gr_value == '1' and lang==1:
                asset_type = "Saham"
  
            if pos_value == "s" and lang==0:
                pos_value = "SELL"
            elif pos_value == "s" and lang==1:
                pos_value = "JUAL"
            elif pos_value == "b" and lang==0:
                pos_value = "BUY"
            elif pos_value == "b" and lang==1:
                pos_value = "BELI"
              
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
                "price": price_value,
                "lang": lang
            }
          

            return jsonify(updated_data)

    return jsonify({})

#---4. Send data to db:
def send_data(data):
    user_id = data.replace('\n', '').strip()

    with engine.connect() as conn:
        # Insert the treatment, ID, round, transaction, initial asset, and other values into the 'responses' table
        conn.execute(
            text("INSERT INTO `teg-simulation-sandbox`.`responses`(`round`,`gr`, `id`, `trx`, `crypto`, `fiat`, `buy`, `sell`, `pos`, `t_gain`,`r_gain`,`t_tax`,`tax_disclos`,`audit`,`t_gain_net`,`r_gain_net`,`r_tax`,`sec`,`price`,`crypto_prev`, `fiat_prev`,`buy_prev`,`r_gain_prev`, `r_tax_prev`)VALUES ('1', :treatment, :id, '0', '1.00', '0', '0', '0','s','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0')"), {"treatment": treatment, "id": random_id})
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



