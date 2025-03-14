from sqlalchemy import create_engine, text
import os
import random
import string
from flask import jsonify
from datetime import datetime

# SQLite connection (relative path to database.db in Replit)
db_path = os.path.join(os.path.dirname(__file__), 'database.db')
engine = create_engine(f'sqlite:///{db_path}')

#----0.1 Assign treatment based on language selection
def insert_group_lang(lang):
    with engine.connect() as conn:
        while True:
            # Generate a random 2-character ID
            random_id = ''.join(random.choices(string.ascii_uppercase +
                                               string.ascii_lowercase + string.digits,
                                               k=2))
            # Check if the generated ID already exists
            result = conn.execute(
                text("SELECT id FROM log WHERE id = :random_id"),
                {'random_id': random_id}
            )
            if not result.fetchone():
                break

        # Convert lang to integer (0 for English, 1 for Indonesian)
        lang_value = 1 if lang == 'Indonesian' else 0

        # Fetch the last entry for the given language
        last_entry = conn.execute(
            text("SELECT gr, lang FROM log WHERE lang = :lang ORDER BY num DESC LIMIT 1"),
            {'lang': lang_value}
        ).fetchone()

        # Determine treatment (alternate between '1' and '2')
        treatment = '2' if last_entry and last_entry[0] == '1' else '1'

        # Fetch the last 'au' value for the determined treatment
        last_au = conn.execute(
            text("SELECT au FROM log WHERE gr = :treatment ORDER BY num DESC LIMIT 1"),
            {'treatment': treatment}
        ).fetchone()
        au_value = 1 if last_au and last_au[0] == 0 else 0

        # Insert the new log entry
        conn.execute(
            text("INSERT INTO log (counter, gr, id, lang, au) VALUES (:counter, :treatment, :id, :lang, :au)"),
            {"counter": 1, "treatment": treatment, "id": random_id, "lang": lang_value, "au": au_value}
        )
        conn.commit()  # Commit the transaction

        # Return treatment dictionary
        return {"treatment": treatment, "id": random_id, "lang": lang_value, "au": au_value}

#----1. Assign random to treatment, start inserting initial data to db
def insert_group_treatment(gr, id, lang):
    with engine.connect() as conn:
        print(f"DEBUG: Inserting into responses: gr={gr}, id={id}, lang={lang}")
        try:
            conn.execute(
                text("""
                    INSERT INTO responses (round, gr, id, lang, trx, crypto, fiat, buy, sell, pos, 
                    t_gain, r_gain, t_tax, tax_disclos, audit, t_gain_net, r_gain_net, r_tax, sec, 
                    price, crypto_prev, fiat_prev, buy_prev, r_gain_prev, r_tax_prev)
                    VALUES (:round, :gr, :id, :lang, :trx, :crypto, :fiat, :buy, :sell, :pos, 
                    :t_gain, :r_gain, :t_tax, :tax_disclos, :audit, :t_gain_net, :r_gain_net, :r_tax, 
                    :sec, :price, :crypto_prev, :fiat_prev, :buy_prev, :r_gain_prev, :r_tax_prev)
                """),
                {
                    "round": 0, "gr": gr, "id": id, "lang": lang, "trx": 0, "crypto": 1.00, "fiat": 0,
                    "buy": 0, "sell": 0, "pos": 's', "t_gain": 0, "r_gain": 0, "t_tax": 0,
                    "tax_disclos": 0, "audit": 0, "t_gain_net": 0, "r_gain_net": 0, "r_tax": 0,
                    "sec": 0, "price": 0, "crypto_prev": 0, "fiat_prev": 0, "buy_prev": 0,
                    "r_gain_prev": 0, "r_tax_prev": 0
                }
            )
            conn.commit()  # Commit the transaction
            print(f"DEBUG: Successfully inserted id={id} into responses")
        except Exception as e:
            print(f"ERROR: Failed to insert into responses: {e}")
            conn.rollback()  # Rollback on error

#----1a. Insert participant profile
def insert_demog(gender, age, education_level, current_education, country_residence, citizenship, 
                asset_experience, tax_experience, description, id):
    with engine.connect() as conn:
        conn.execute(
            text("""
                INSERT INTO demog (gender, age, education_level, current_education, country_residence, 
                citizenship, asset_experience, tax_experience, description, id)
                VALUES (:gender, :age, :education_level, :current_education, :country_residence, 
                :citizenship, :asset_experience, :tax_experience, :description, :id)
            """),
            {
                "gender": gender, "age": age, "education_level": education_level,
                "current_education": current_education, "country_residence": country_residence,
                "citizenship": citizenship, "asset_experience": asset_experience,
                "tax_experience": tax_experience, "description": description, "id": id
            }
        )
        conn.commit()  # Commit the transaction

#----2. Fetch initial game data from db 
def fetch_init_data(id):
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT round, gr, id, trx, crypto, fiat, buy, sell, pos, t_gain, r_gain, t_tax, 
                crypto_prev, fiat_prev, buy_prev, r_tax, r_gain_net, t_gain_net, r_gain_prev, 
                r_tax_prev, tax_disclos, tax_discre, audit, penalty, r_gain_final, lang 
                FROM responses WHERE id = :id ORDER BY ts DESC LIMIT 1
            """),
            {"id": id}
        )
        row = result.fetchone()
        if row:
            data = dict(row._mapping)  # Convert to dictionary
            lang = data['lang']
            asset_type = {
                ('2', 0): "Crypto", ('2', 1): "Kripto",
                ('1', 0): "Stock", ('1', 1): "Saham"
            }.get((data['gr'], lang), None)

            pos_map = {
                's': {0: "SELL", 1: "JUAL"},
                'b': {0: "BUY", 1: "BELI"}
            }
            data['pos'] = pos_map.get(data['pos'], {}).get(lang, data['pos'])
            data['crypto'] = "{:,.2f}".format(data['crypto']).replace(",", "X").replace(".", ",").replace("X", ".") if lang == 1 else str(data['crypto'])
            data['asset_type'] = asset_type
            return data
        return None

#----3. Retrieve data from db 
def retrieve_data(id):
    user_id = id.strip()
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT round, gr, id, trx, crypto, fiat, buy, sell, pos, t_gain, r_gain, t_tax, 
                crypto_prev, fiat_prev, buy_prev, r_tax, r_gain_net, t_gain_net, r_gain_prev, 
                r_tax_prev, tax_disclos, tax_discre, audit, penalty, r_gain_final, sec, price, lang 
                FROM responses WHERE id = :id ORDER BY ts DESC LIMIT 1
            """),
            {"id": user_id}
        )
        row = result.fetchone()
        if row:
            data = dict(row._mapping)
            lang = data['lang']
            asset_type = {
                ('2', 0): "Crypto", ('2', 1): "Kripto",
                ('1', 0): "Stock", ('1', 1): "Saham"
            }.get((data['gr'], lang), None)

            pos_map = {
                's': {0: "SELL", 1: "JUAL"},
                'b': {0: "BUY", 1: "BELI"}
            }
            data['pos'] = pos_map.get(data['pos'], {}).get(lang, data['pos'])
            data['asset_type'] = asset_type
            return jsonify(data)
        return jsonify({})

#----4. Send data to db (Note: This function seems unused in your original code; included for completeness)
def send_data(data):
    user_id = data.strip()
    with engine.connect() as conn:
        # Assuming 'treatment' and 'random_id' should come from the data parameter; adjust as needed
        treatment = '1'  # Default value; modify based on your logic
        random_id = user_id  # Using the provided data as ID
        conn.execute(
            text("""
                INSERT INTO responses (round, gr, id, trx, crypto, fiat, buy, sell, pos, t_gain, 
                r_gain, t_tax, tax_disclos, audit, t_gain_net, r_gain_net, r_tax, sec, price, 
                crypto_prev, fiat_prev, buy_prev, r_gain_prev, r_tax_prev)
                VALUES (:round, :gr, :id, :trx, :crypto, :fiat, :buy, :sell, :pos, :t_gain, 
                :r_gain, :t_tax, :tax_disclos, :audit, :t_gain_net, :r_gain_net, :r_tax, :sec, 
                :price, :crypto_prev, :fiat_prev, :buy_prev, :r_gain_prev, :r_tax_prev)
            """),
            {
                "round": 1, "gr": treatment, "id": random_id, "trx": 0, "crypto": 1.00, "fiat": 0,
                "buy": 0, "sell": 0, "pos": 's', "t_gain": 0, "r_gain": 0, "t_tax": 0,
                "tax_disclos": 0, "audit": 0, "t_gain_net": 0, "r_gain_net": 0, "r_tax": 0,
                "sec": 0, "price": 0, "crypto_prev": 0, "fiat_prev": 0, "buy_prev": 0,
                "r_gain_prev": 0, "r_tax_prev": 0
            }
        )
        conn.commit()  # Commit the transaction
        return {"treatment": treatment, "id": random_id}

#----5. Fetch updated data (for completeness, though not heavily used in your original code)
def fetch_update_data(id):
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT round, gr, id, trx, crypto, fiat, buy, sell, pos, t_gain, r_gain, t_tax, 
                crypto_prev, fiat_prev, buy_prev, r_tax, r_gain_net, t_gain_net, r_gain_prev, 
                r_tax_prev, tax_disclos, tax_discre, audit, penalty, r_gain_final 
                FROM responses WHERE id = :id ORDER BY ts DESC LIMIT 1
            """),
            {"id": id}
        )
        row = result.fetchone()
        if row:
            data = dict(row._mapping)
            asset_type = "Crypto" if data['gr'] == '2' else "Stock" if data['gr'] == '1' else None
            data['pos'] = "SELL" if data['pos'] == 's' else "BUY" if data['pos'] == 'b' else data['pos']
            data['asset_type'] = asset_type
            return data
        return None

#----6. Load group treatment (for debugging or testing)
def load_group_treatment():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM log"))
        print(result.fetchall())

# Optional: Test the database connection
if __name__ == "__main__":
    load_group_treatment()  # Example test function