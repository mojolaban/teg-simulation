from flask import Flask, redirect, render_template, request, jsonify, session, url_for
from database import engine, insert_group_treatment, fetch_init_data, retrieve_data, insert_demog, insert_group_lang
from sqlalchemy import text
from datetime import datetime
from decimal import Decimal
import json
import random

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/select_language', methods=['POST'])
def select_language():
    language = request.form.get('language')
    # Call insert_group_treatment function to insert the language into the database
    # and retrieve the treatment dictionary
    treatment_dict = insert_group_lang(language)
    id=treatment_dict["id"]
    treatment=treatment_dict["treatment"]
    lang=treatment_dict["lang"]
    if language == 'English':
        # Pass the treatment dictionary to the render_template function
        print(treatment_dict["id"])
        return render_template('home.html', id=id, treatment=treatment, lang=lang)
    elif language == 'Indonesian':
        # Pass the treatment dictionary to the render_template function
        return render_template('home-a.html', id=id, treatment=treatment, lang=lang)
    # If somehow an invalid option is submitted, reload the page
    return render_template('index.html')

  

#-----After home page, assign group and insert init data
@app.route("/form_demog", methods=['GET', 'POST'])
def form_demog():
    # Determine the method and retrieve parameters accordingly
    if request.method == 'POST':
        lang_value = request.form.get('lang')
        treatment_value = request.form.get('treatment')
        id_value = request.form.get('id')
    else:  # GET method
        lang_value = request.args.get('lang')
        treatment_value = request.args.get('treatment')
        id_value = request.args.get('id')


  # Debug statement to print the values in the server console
    print("Debug - ID:", id_value, "Treatment:", treatment_value, "Language:", lang_value)


    if treatment_value == "1" and lang_value == "1":
        asset_type = 'stock'
        return render_template('form_demog-a.html', id=id_value, asset_type=asset_type, lang=lang_value)
    elif treatment_value == "1" and lang_value == "0":
        asset_type = 'stock'
        return render_template('form_demog.html', id=id_value, asset_type=asset_type, lang=lang_value)
    elif treatment_value == "2" and lang_value == "1":
        asset_type = 'crypto'
        return render_template('form_demog-a.html', id=id_value, asset_type=asset_type, lang=lang_value)
    elif treatment_value == "2" and lang_value == "0":
        asset_type = 'crypto'
        return render_template('form_demog.html', id=id_value, asset_type=asset_type, lang=lang_value)
    else:
        # You might want to return a proper error response here
        return "Error"


#----Insert into instructions page
@app.route("/instructions", methods=['GET', 'POST'])
def instructions():
    if request.method == 'POST':
        gender = request.form['gender']
        age = request.form['age']
        education_level = request.form['education_level']
        current_education = request.form['current_education']
        country_residence = request.form['country_residence']
        citizenship = request.form['citizenship']
        asset_experience = ','.join(request.form.getlist('asset_experience[]'))
        tax_experience = request.form['tax_experience']
        description = request.form['description']
        id = request.form['id']
        asset_type = request.form['asset_type']
        lang = request.form['lang']

        insert_demog(gender, age, education_level, current_education, country_residence, citizenship, asset_experience, tax_experience, description, id)
        if 'stock' in asset_type and lang == "0":
          print("ID:", id)  # Debug statement
          print("asset_type:", asset_type)  # Debug statement
          print("language:", lang)  # Debug statement
          return render_template('instruction-1.html', id=id, asset_type=asset_type, lang=lang)
        elif 'stock' in asset_type and lang == "1":
          print("ID:", id)  # Debug statement
          print("asset_type:", asset_type)  # Debug statement
          print("language:", lang)  # Debug statement
          return render_template('instruction-1-a.html', id=id, asset_type=asset_type, lang=lang)
        elif 'crypto' in asset_type and lang == "0":
          print("ID:", id)  # Debug statement
          print("asset_type:", asset_type)  # Debug statement
          print("language:", lang)  # Debug statement
          return render_template('instruction-2.html', id=id, asset_type=asset_type, lang=lang)
        elif 'crypto' in asset_type and lang =="1":
          print("ID:", id)  # Debug statement
          print("asset_type:", asset_type)  # Debug statement
          print("language:", lang)  # Debug statement
          return render_template('instruction-2-a.html', id=id, asset_type=asset_type, lang=lang)


    elif request.method == 'GET':
        gender = request.args.get('gender')
        age = request.args.get('age')
        education_level = request.args.get('education_level')
        current_education = request.args.get('current_education')
        country_residence = request.args.get('country_residence')
        citizenship = request.args.get('citizenship')
        asset_experience = request.args.get('asset_experience[]')
        tax_experience = request.args.get('tax_experience')
        description = request.args.get('description')
        id = request.args.get('id')
        asset_type = request.args.get('asset_type')
        lang = request.args.get('lang')

        if gender and age and education_level and current_education and country_residence and citizenship and asset_experience and tax_experience and description and id and asset_type:
            insert_demog(gender, age, education_level, current_education, country_residence, citizenship, asset_experience, tax_experience, description, id)

            if 'stock' in asset_type and lang == "1":
                return render_template('instruction-1.html', id=id, asset_type=asset_type, lang=lang)
            elif 'stock' in asset_type and lang =="0":
                return render_template('instruction-1-a.html', id=id, asset_type=asset_type, lang=lang)
            elif 'crypto' in asset_type and lang == "1":
                return render_template('instruction-2.html', id=id, asset_type=asset_type, lang=lang)
            elif 'crypto' in asset_type and lang =="0":
                return render_template('instruction-2-a.html', id=id, asset_type=asset_type, lang=lang)
            else:
                # Handle other cases if needed
                pass
        else:
            # Handle case where not all data is provided
            return render_template('form_demog.html')



#----Insert initial game data from db to try out instruction
@app.route("/tryout", methods=['GET', 'POST'])
def tryout():
  if request.method == 'POST':
    lang = request.form['lang']
    id = request.form['id']
    asset_type = request.form['asset_type']
    if asset_type == "stock":
        gr = "1"
    elif asset_type == "crypto":
        gr = "2"
    else:
        gr = "unknown"
    insert_group_treatment(gr,id,lang)
    if 'stock' in asset_type and lang=="0":
          print("ID:", id)  # Debug statement
          print("asset_Type:", asset_type)  # Debug statement
          print("language:", lang)  # Debug statement
          return render_template('instruction-tryout-1.html', id=id, asset_type=asset_type, lang=lang)
    elif 'stock' in asset_type and lang=="1":
          print("ID:", id)  # Debug statement
          print("asset_Type:", asset_type)  # Debug statement
          print("language:", lang)  # Debug statement
          return render_template('instruction-tryout-1-a.html', id=id, asset_type=asset_type, lang=lang)
    elif 'crypto' in asset_type and lang=="0":
          print("ID:", id)  # Debug statement
          print("asset_Type:", asset_type)  # Debug statement
          print("language:", lang)  # Debug statement
          return render_template('instruction-tryout-2.html', id=id, asset_type=asset_type, lang=lang)
    elif 'crypto' in asset_type and lang=="1":
          print("ID:", id)  # Debug statement
          print("asset_Type:", asset_type)  # Debug statement
          print("language:", lang)  # Debug statement
          return render_template('instruction-tryout-2-a.html', id=id, asset_type=asset_type, lang=lang)
    else:
          # Handle unsupported asset types
          return "Unsupported asset type"

  elif request.method == 'GET':
      id = request.args.get('id')
      asset_type = request.args.get('asset_type')
      lang = request.args.get('lang')
      if asset_type == "stock":
          gr = "1"
      elif asset_type == "crypto":
          gr = "2"
      else:
          gr = "unknown"
      insert_group_treatment(gr,id)
      if asset_type == "stock" and lang=="0":
          print("ID:", id)  # Debug statement
          print("asset_Type:", asset_type)  # Debug statement
          print("language:", lang)  # Debug statement
          return render_template('instruction-tryout-1.html', id=id, asset_type=asset_type, lang=lang)
      elif asset_type == "stock" and lang=="1":
          print("ID:", id)  # Debug statement
          print("asset_Type:", asset_type)  # Debug statement
          print("language:", lang)  # Debug statement
          return render_template('instruction-tryout-1-a.html', id=id, asset_type=asset_type, lang=lang)
      elif asset_type == "crypto" and lang=="0":
          print("ID:", id)  # Debug statement
          print("asset_Type:", asset_type)  # Debug statement
          print("language:", lang)  # Debug statement
          return render_template('instruction-tryout-2.html', id=id, asset_type=asset_type, lang=lang)
      elif asset_type == "crypto" and lang=="1":
          print("ID:", id)  # Debug statement
          print("asset_Type:", asset_type)  # Debug statement
          print("language:", lang)  # Debug statement
          return render_template('instruction-tryout-2-a.html', id=id, asset_type=asset_type, lang=lang)
      else:
          # Handle unsupported asset types
          return "Unsupported asset type"
  
# Custom Jinja filter
def format_crypto(value, lang):
    if isinstance(value, Decimal):
        # Format based on language
        if lang == 1:  # Indonesian
            return "{:,.2f}".format(value).replace(",", "X").replace(".", ",").replace("X", ".")
        else:  # Default to English
            return "{:,.2f}".format(value)
    return value

app.jinja_env.filters['format_crypto'] = format_crypto


#----Insert initial game data from db to html
@app.route("/start", methods=['GET', 'POST'])
def starting_game():
    if request.method == 'POST':
        id = request.form.get('id')
        lang = request.form.get('lang')
        print("ID:", id)  # Debug statement
        print("language:", lang)  # Debug statement
        if id:
            init_data = fetch_init_data(id)
            print("Init Data:", init_data)  # Debug statement
            if init_data and lang == "0":
                return render_template('round0.html', data=init_data)
            elif init_data and lang == "1":
              return render_template('round0-a.html', data=init_data)
        return "Error: Invalid ID"
    elif request.method == 'GET':
        # Handle GET requests (if needed)
        id = request.form.get('id')
        lang = request.form.get('lang')
        print("ID:", id)  # Debug statement
        print("language:", lang)  # Debug statement
        if id:
            init_data = fetch_init_data(id)
            print("Init Data:", init_data)  # Debug statement
            if init_data and lang=="0":
              return render_template('round0.html', data=init_data)  # Example template to render for GET requests
            elif init_data and lang=="1":
              return render_template('round0-a.html', data=init_data)  # Example template to render for GET requests 
        return "Error: Invalid ID"
      

       
#-----Start interacting with the data inside the game
#-----Send data to the database

@app.route("/sendData", methods=['POST'])
def send_games_data():
  data = request.get_json()
  timer_value = data.get('timerValue')
  lang = data.get('lang')
#  price_value = data.get('priceValue').replace(',', '')
  price_value = data.get('priceValue', '').replace(',', '').replace('.', '')

  if not price_value:
      price_value = 0 
  
  user_id = data.get('userid').replace('\n', '').strip()
  group_id = data.get('groupid').replace('\n', '').strip()
  # Assuming data.get('posValue') returns a string
  pos_value_str = data.get('posValue', '').replace('\n', '').strip()  # Clean the string
  
  # Map "JUAL" to "SELL" and "BELI" to "BUY"
  if pos_value_str == "JUAL":
      pos_value = "b"
  elif pos_value_str == "BELI":
      pos_value = "s"
  else:
      pos_value = pos_value_str  # Use the original value if it's neither "JUAL" nor "BELI"
  
  trx_value = data.get('trxValue')
  round_value = data.get('roundValue')
  
#  crypto_prev_value = data.get('cryptoPrevValue').replace('\n', '').strip()
  
  crypto_prev_value_raw = data.get('cryptoPrevValue')  
  # Check if the value is a string and clean it; otherwise, handle it as an integer
  if isinstance(crypto_prev_value_raw, str):
      crypto_prev_value = crypto_prev_value_raw.replace('\n', '').strip()
  else:  # If it's not a string, assume it's an integer
      crypto_prev_value = crypto_prev_value_raw  # Use the integer value directly  
    
  fiat_prev_value = data.get('fiatPrevValue')
#  crypto_value = data.get('cryptoValue').replace('\n', '').strip()
  crypto_value_raw = data.get('cryptoValue')  
  # Check if the value is a string and clean it; otherwise, handle it as an integer
  if isinstance(crypto_value_raw, str):
      crypto_value = crypto_value_raw.replace('\n', '').strip()
  else:  # If it's not a string, assume it's an integer
      crypto_value = crypto_value_raw  # Use the integer value directly  

  #  fiat_value = data.get('fiatValue').replace('\n', '').strip()
  fiat_value_raw = data.get('fiatValue')  
  # Check if the value is a string and clean it; otherwise, handle it as an integer
  if isinstance(fiat_value_raw, str):
      fiat_value = fiat_value_raw.replace('\n', '').strip()
  else:  # If it's not a string, assume it's an integer
      fiat_value = fiat_value_raw  # Use the integer value directly   

#  fiat_value = data.get('fiatValue')  
  
  buy_prev_value = data.get('buyPrevValue')
#  sell_value = data.get('sellValue').replace('\n', '').strip()
  sell_value_raw = data.get('sellValue')
  # Check if the value is a string and clean it; if it's an integer, use it directly
  if isinstance(sell_value_raw, str):
      sell_value = sell_value_raw.replace('\n', '').strip()
  else:
      sell_value = sell_value_raw
  buy_value = data.get('buyValue')
#  t_gain_value = data.get('tGainValue').replace('\n', '').strip()
  t_gain_value_raw = data.get('tGainValue')
  # Check if the value is a string and clean it; otherwise, handle it as an integer
  if isinstance(t_gain_value_raw, str):
      t_gain_value = t_gain_value_raw.replace('\n', '').strip()
  else:  # If it's not a string, assume it's an integer
      t_gain_value = t_gain_value_raw  # Use the integer value directly
  t_tax_value_raw = data.get('tTaxValue')
  # Check if the value is a string and clean it; otherwise, handle it as an integer
  if isinstance(t_tax_value_raw, str):
    t_tax_value = t_tax_value_raw.replace('\n', '').strip()
  else:  # If it's not a string, assume it's an integer
    t_tax_value = t_tax_value_raw  # Use the integer value directly
    
#  t_gain_net_value = data.get('tGainNetValue').replace('\n', '').strip()
  t_gain_net_value_raw = data.get('tGainNetValue')
  # Determine the type and proceed accordingly
  if isinstance(t_gain_net_value_raw, str):
      # If it's a string, strip newlines and whitespace
      t_gain_net_value = t_gain_net_value_raw.replace('\n', '').strip()
  else:
      # If it's an integer (or any non-string), use it directly
      t_gain_net_value = t_gain_net_value_raw
  r_gain_value = data.get('rGainValue')
  r_gain_prev_value = data.get('rGainPrevValue')
  r_tax_value = data.get('rTaxValue')
  r_tax_prev_value = data.get('rTaxPrevValue')
  r_gain_net_value = str(data.get('rGainNetValue'))
  r_gain_net_value = r_gain_net_value.replace('\n', '').strip()
#  tax_discre_value = data.get('taxDiscreValue')
  tax_disclos_value =data.get('taxDisclosValue')
  audit_value =data.get('auditValue')
#  penalty_value =data.get('penaltyValue')
#  r_gain_final_value =data.get('rGainFinalValue')
  
  with engine.connect() as conn:
    conn.execute(text("INSERT INTO `teg-simulation-sandbox`.`responses` (`sec`,`price`,`id`, `gr`, `pos`, `trx`, `round`, `crypto_prev`, `fiat_prev`,`crypto`, `fiat`, `buy_prev`, `buy`, `sell`, `t_gain`,`t_tax`, `t_gain_net`, `r_gain`, `r_gain_prev`, `r_tax`, `r_tax_prev`, `r_gain_net`, `tax_disclos`,`audit`, `lang`) VALUES (:sec, :price, :id, :gr, :pos, :trx, :round, :crypto_prev, :fiat_prev, :crypto, :fiat, :buy_prev,:buy, :sell, :t_gain, :t_tax, :t_gain_net, :r_gain, :r_gain_prev, :r_tax, :r_tax_prev, :r_gain_net, :tax_disclos,:audit,:lang)"), {"sec": timer_value, "price": price_value, "id": user_id, "gr" : group_id, "pos" : pos_value, "trx" : trx_value, "round" : round_value, "crypto_prev" :crypto_prev_value,  "fiat_prev" :fiat_prev_value, "crypto" :crypto_value,  "fiat" :fiat_value, "buy_prev":buy_prev_value,"buy":buy_value, "sell":sell_value, "t_gain":t_gain_value, "t_tax":t_tax_value, "t_gain_net": t_gain_net_value, "r_gain": r_gain_value, "r_gain_prev": r_gain_prev_value, "r_tax": r_tax_value, "r_tax_prev": r_tax_prev_value,"r_gain_net": r_gain_net_value,"tax_disclos": tax_disclos_value,"audit": audit_value, "lang": lang})
    print(f"Sending Data:")
    print(f"Timer Value: {timer_value}")
    print(f"Price Value: {price_value}")
    print(f"User ID: {user_id}")
    print(f"Group ID: {group_id}")
    print(f"Pos Value: {pos_value}")
    print(f"Trx Value: {trx_value}")
    print(f"Round Value: {round_value}")
    print(f"Crypto_Prev Value: {crypto_prev_value}")
    print(f"Fiat_Prev Value: {fiat_prev_value}")
    print(f"Crypto Value: {crypto_value}")
    print(f"Fiat Value: {fiat_value}")
    print(f"Buy_Prev Value: {buy_prev_value}")
    print(f"Buy Value: {buy_value}")
    print(f"Sell Value: {sell_value}")
    print(f"T_Gain Value: {t_gain_value}")
    print(f"T_Tax Value: {t_tax_value}")
    print(f"Trx Gain Net Value: {t_gain_net_value}")
    print(f"Rnd Gain Value: {r_gain_value}")
    print(f"Rnd Gain_Prev Value: {r_gain_prev_value}")
    print(f"Rnd Tax Value: {r_tax_value}")
    print(f"Rnd Tax_Prev Value: {r_tax_prev_value}")
    print(f"Rnd Gain Net Value: {r_gain_net_value}")
    print(f"Tax Disclos Value: {tax_disclos_value}")
    print(f"Audit Value: {audit_value}")
    print(f"Language: {lang}")

    result = conn.execute(text("SELECT round, gr, id, trx, crypto, fiat, buy, sell, pos, t_gain, r_gain, t_tax, crypto_prev, fiat_prev, buy_prev, r_tax, r_gain_net, t_gain_net, r_gain_prev, r_tax_prev, tax_disclos, tax_discre, audit, penalty, r_gain_final, lang FROM responses WHERE id = :id ORDER BY ts DESC LIMIT 1;"), {"id": user_id})
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

            asset_type = "Unknown" 
            if gr_value == '2' and lang == 0:
                asset_type = "Crypto"
            elif gr_value == '2' and lang == 1:
                asset_type = "Kripto"
            elif gr_value == '1' and lang == 0:
                asset_type = "Stock"
            elif gr_value == '1' and lang == 1:
                asset_type = "Saham"
              
            if trx_value < 5:
                if pos_value == "s" and lang == 0:
                    pos_value = "SELL"
                elif pos_value == "s" and lang == 1:
                    pos_value = "JUAL"
                elif pos_value == "b" and lang == 0:
                    pos_value = "BUY"
                elif pos_value == "b" and lang == 1:
                    pos_value = "BELI"
            else:
                pos_value = "STOP"

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
            print("Retrieved Data:")
            print(updated_data)
            return jsonify(updated_data)


#----Insert data to tax reporting page
@app.route("/tr")
def tax_reporting():     
    user_id = request.args.get('id')
    response = retrieve_data(user_id)
    response_data =  response.json  # Convert the content to a dictionary
    print("Summary Data:", response_data)
    print("Language:",  response_data['lang'])
    # Determine the template based on the language
    template_name = 'tax_reporting-a.html' if response_data['lang'] == 1 else 'tax_reporting.html'
    # Check for valid ID indirectly by ensuring 'lang' is present and correctly set
    if 'lang' in response_data and response_data['lang'] in [0, 1]:
        return render_template(template_name, summary_data=response_data)
    else:
        return "Error: Invalid ID"
  
#----Sending data from tax reporting page to db, then show them to audit page
@app.route("/tax_disclosure", methods=["GET","POST"])
def tax_disclosure():
    if request.method == "POST":
      # Handling POST request data
      userid = request.form.get('id')
      lang = request.form.get('lang')
      taxdisclos = request.form.get('tax_disclos', '').replace(',', '')
      audit_value = 0 if random.random() < 0.8 else 1  # 20% chance of audit

      if not userid or not lang or taxdisclos is None:
          return "Missing data", 400  # Bad Request
        
      print("Reported Data:")
      print(f"UserID: {userid}, Audit: {audit_value}, Tax Disclos: {taxdisclos}, Lang: {lang}")

      with engine.begin() as conn:  # Use 'begin()' for automatic transaction management
          update_statement = text("""
              UPDATE `teg-simulation-sandbox`.`responses`
              SET `tax_disclos` = :new_tax_disclos_value, `audit` = :audit_value
              WHERE `id` = :user_id
              ORDER BY `ts` DESC
              LIMIT 1
          """)
          conn.execute(update_statement, {"new_tax_disclos_value": taxdisclos, "audit_value": audit_value, "user_id": userid})

          select_statement = text("""
              SELECT `round`, `audit`
              FROM `teg-simulation-sandbox`.`responses`
              WHERE `id` = :user_id
              ORDER BY `ts` DESC
              LIMIT 1
          """)
          result = conn.execute(select_statement, {"user_id": userid})
          latest_round, latest_audit = result.fetchone()

      print("Latest Data:", f"Round: {latest_round}, Audit: {latest_audit}")

    elif request.method == "GET":
      # Handling GET request data, if necessary
      # You can access GET parameters with request.args
      userid = request.args.get('id')
      lang = request.args.get('lang')
      taxdisclos = request.args.get('tax_disclos', '').replace(',', '')
      audit_value = 0 if random.random() < 0.8 else 1  # 20% chance of audit

      with engine.begin() as conn:  # Use 'begin()' for automatic transaction management
          update_statement = text("""
              UPDATE `teg-simulation-sandbox`.`responses`
              SET `tax_disclos` = :new_tax_disclos_value, `audit` = :audit_value
              WHERE `id` = :user_id
              ORDER BY `ts` DESC
              LIMIT 1
          """)
          conn.execute(update_statement, {"new_tax_disclos_value": taxdisclos, "audit_value": audit_value, "user_id": userid})

          select_statement = text("""
              SELECT `round`, `audit`
              FROM `teg-simulation-sandbox`.`responses`
              WHERE `id` = :user_id
              ORDER BY `ts` DESC
              LIMIT 1
          """)
          result = conn.execute(select_statement, {"user_id": userid})
          latest_round, latest_audit = result.fetchone()

      print("Latest Data:", f"Round: {latest_round}, Audit: {latest_audit}")
        
    # Example conditional rendering based on `latest_audit` and `lang`
    # Assuming `latest_audit` and `lang` are determined inside your function
    template_name = f"tax_audit_{'1' if latest_audit == 1 else '0'}{'-a' if lang == '1' else ''}.html"
    response_data = retrieve_data(userid).json
    return render_template(template_name, summary_data=response_data)

#----Sending data from tax audit page to db, initiate new round then go to rounds 
@app.route("/next_round") #, methods=["POST"]) 
def next_round():
    data = request.args
    userid = (data['id'])
    lang = (data['lang'])
    print("Next Round Data:")
    print(f"UserID: {userid}")

    with engine.connect() as conn:
        select_statement = text("""
            SELECT `round`, `gr` 
            FROM `teg-simulation-sandbox`.`responses`
            WHERE `id` = :user_id
            ORDER BY `ts` DESC
            LIMIT 1
        """)
        result = conn.execute(select_statement, {"user_id": userid})
        latest_round, gr = result.fetchone()

        if latest_round < 15:
          next_round = latest_round + 1
          conn.execute(
              text("INSERT INTO `teg-simulation-sandbox`.`responses`(`round`,`gr`, `id`, `trx`, `crypto`, `fiat`, `buy`, `sell`, `pos`, `t_gain`, `r_gain`, `t_tax`, `tax_disclos`, `audit`, `t_gain_net`, `r_gain_net`,`r_tax`,`sec`,`price`,`crypto_prev`, `fiat_prev`, `buy_prev`, `r_gain_prev`,`r_tax_prev`, `lang`)VALUES (:round, :gr, :id, '0', '1.00', '0', '0', '0','s','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0',:lang)"),
              {"round": next_round, "gr": gr, "id": userid, "lang": lang}
          )
          init_data = fetch_init_data(userid) # Removed curly braces around userid for correct function call
          if init_data:
              # Check the lang value and return the appropriate template
              if lang == '0':
                  return render_template('rounds.html', data=init_data)
              elif lang == '1':
                  return render_template('rounds-a.html', data=init_data)
    
        else:
            random_number = random.randint(1, 15)

            select_statement_2 = text("""
                SELECT `id`, `gr`,`round`, `r_gain_final`, `lang`
                FROM `teg-simulation-sandbox`.`responses`
                WHERE `id` = :user_id AND `round` = :random_number
            """)
            result_2 = conn.execute(select_statement_2, {"user_id": userid, "random_number": random_number})
            result = result_2.fetchone()

            # Check if the result is None
            if result is None:
                # Handle the case when no data is found
                print("No data found in select_statement_2")
                return "No data found"

            user_id, gr, comp_round, comp_amt, lang = result
            
            # Modify compensation logic based on lang value
            if lang == 0:
                if comp_amt < 1000000:
                    comp_rgainfinal = 5
                elif 1000000 <= comp_amt <= 5000000:
                    comp_rgainfinal = 10
                else:
                    comp_rgainfinal = 20
            elif lang == 1:
                if comp_amt < 1000000:
                    comp_rgainfinal = 50000
                elif 1000000 <= comp_amt <= 5000000:
                    comp_rgainfinal = 100000
                else:
                    comp_rgainfinal = 200000
            
            print("Compensation:")
            print(f"UserID: {user_id}")
            print(f"Group: {gr}")
            print(f"Round: {comp_round}")
            print(f"Round Gain Amount: {comp_amt}")
            print(f"Compensation Amount: {comp_rgainfinal}")
            print(f"Lang: {lang}")
            
            # Return the appropriate template based on lang value
            if lang == 0:
                return render_template("the_random_picker.html", user_id=user_id, comp_round=comp_round, comp_amt=comp_amt, comp_rgainfinal=comp_rgainfinal, gr=gr, lang=lang)
            elif lang == 1:
                return render_template("the_random_picker-a.html", user_id=user_id, comp_round=comp_round, comp_amt=comp_amt, comp_rgainfinal=comp_rgainfinal, gr=gr, lang=lang)




@app.route('/survey', methods=['GET', 'POST'])
def survey():
    if request.method == 'POST':
      comp_amt = request.form.get('comp_amt')
      comp_round = request.form.get('comp_round')
      comp_rgainfinal = request.form.get('comp_rgainfinal')
      user_id = request.form.get('user_id')
      lang = request.form.get('lang')
      gr = str(request.form.get('gr')).replace('\n', '').strip()[:1]
  
      # Process the data as needed
      with engine.connect() as conn:
          insert_statement = text("""
              INSERT INTO compensation (comp_amt, id, comp_round, comp_rgainfinal, gr, lang)
              VALUES (:comp_amt, :user_id, :comp_round, :comp_rgainfinal, :gr, :lang)
          """)
          conn.execute(
              insert_statement,
              {"comp_amt": comp_amt, "user_id": user_id, "comp_round": comp_round, "comp_rgainfinal": comp_rgainfinal, "gr": gr, "lang": lang}
          )

      
      print("Recorded compensation:")
      print(f"UserID: {user_id}")
      print(f"Group: {gr}")
      print(f"CompAmt: {comp_amt}")
      print(f"CompRound: {comp_round}")
      print(f"CompRoundGain: {comp_rgainfinal}")
      print(f"Lang: {lang}")
  

  
    questions = [
        ' ... because to me it’s obvious that this is what you do.',
        '... even if tax audits did not exist.',
        '... without spending a long time thinking how I could reduce them.',
        'I feel that I am forced to pay my taxes.',        
        'I pay my taxes because the risk of being checked is too high.',     
        'I pay taxes for I don`t know how to evade taxes without attracting attention.',  
        'Tax officers pass information in an understandable way.',        
        'Tax officers know exactly how a correct tax file should look like.',        
        'Tax officers inform and advise taxpayers how to pay taxes correctly.',      
        'Tax officers have the legal right to collect taxes.',       
        'Tax officers apply severe punishments.',        
        'Tax officers prosecute taxpayers mainly with audits and fines.',   
        'Tax officers enforce compliance through audits and fines.',
        'I trust tax officers without thinking about it.',        
        'I trust tax officers automatically.',        
        'I trust tax officers usually without dealing with it deeply.',        
        'I trust the tax officers because the political and economic situation enables them to work professionally.',
        'I trust the tax officers because they accomplish their work very well and competently.',
        'I trust the tax officers because they are benevolent to taxpayers.',        
        'I trust the tax officers because the tax officers pursue important goals for the country.',        
        'Most other taxpayers are paying their taxes correctly without thinking about it.',    
        'Most other taxpayers automatically pay their taxes.',        
        'Most other taxpayers pay their taxes honestly without dealing with it deeply.',       
        'Most other taxpayers pay their taxes honestly because of audits and fines.',        
        'Most other taxpayers pay their taxes honestly because they respect the law.',        
        'Most other taxpayers pay their taxes honestly because they love their country.',      
        'Most other taxpayers pay taxes because they get something in exchange.',        
        ' Most other taxpayers pay taxes because taxes are used for public interests such as education & health.',        
        'Most other taxpayers pay taxes because its a way to close the gap between rich and poor.',        
        'How likley will you pay your taxes for the current year correctly and in full extent to the tax authority?'
        ]

    questindo = [
        '... karena bagi saya jelas ini yang harus Anda lakukan.',
        '... bahkan jika audit pajak tidak ada.',
        '... tanpa menghabiskan waktu lama memikirkan bagaimana saya bisa menguranginya.',
        'Saya merasa bahwa saya dipaksa untuk membayar pajak.',
        'Saya membayar pajak karena risiko diaudit terlalu tinggi.',
        'Saya membayar pajak karena saya tidak tahu cara menghindari pajak tanpa menarik perhatian.',
        'Petugas pajak menyampaikan informasi dengan cara yang mudah dipahami.',
        'Petugas pajak tahu persis bagaimana seharusnya laporan pajak yang benar.',
        'Petugas pajak menginformasikan dan menasihati wajib pajak cara membayar pajak dengan benar.',
        'Petugas pajak memiliki mandat hukum untuk mengumpulkan pajak.',
        'Petugas pajak menerapkan hukuman yang berat.',
        'Petugas pajak memprosekusi wajib pajak terutama dengan audit dan denda.',
        'Petugas pajak memaksa wajib pajak patuh melalui audit dan denda.',
        'Saya mempercayai petugas pajak tanpa memikirkannya.',
        'Saya secara otomatis mempercayai petugas pajak.',
        'Biasanya saya mempercayai petugas pajak tanpa memikirkannya secara mendalam.',
        'Saya mempercayai petugas pajak karena situasi politik dan ekonomi memungkinkan mereka bekerja secara profesional.',
        'Saya mempercayai petugas pajak karena mereka melakukan pekerjaan mereka dengan sangat baik dan kompeten.',
        'Saya mempercayai petugas pajak karena mereka memiliki niatan baik kepada wajib pajak.',
        'Saya mempercayai petugas pajak karena petugas pajak bekerja untuk mencapai tujuan penting bernegara.',
        'Sebagian besar wajib pajak lain membayar pajak mereka dengan benar tanpa memikirkannya.',
        'Sebagian besar wajib pajak lain secara otomatis membayar pajak mereka.',
        'Sebagian besar wajib pajak lain membayar pajak mereka dengan jujur tanpa memikirkannya secara mendalam.',
        'Sebagian besar wajib pajak lain membayar pajak mereka dengan jujur karena audit dan denda.',
        'Sebagian besar wajib pajak lain membayar pajak mereka dengan jujur karena mereka menghormati hukum.',
        'Sebagian besar wajib pajak lain membayar pajak mereka dengan jujur karena mereka mencintai negaranya.',
        'Sebagian besar wajib pajak lain membayar pajak karena mereka mendapatkan sesuatu sebagai imbalannya.',
        'Sebagian besar wajib pajak lain membayar pajak karena pajak digunakan untuk kepentingan publik seperti pendidikan & kesehatan.',
        'Sebagian besar wajib pajak lain membayar pajak sebagai cara untuk menutup kesenjangan antara kaya dan miskin.',
        'Seberapa mungkin Anda akan membayar pajak Anda untuk tahun ini secara benar dan penuh kepada otoritas pajak?'
  ]
    # Depending on the lang, choose the appropriate template and question set
    if lang == '0':
        return render_template('the_survey.html', id=user_id, gr=gr, lang=lang, questions=questions)
    elif lang == '1':
        return render_template('the_survey-a.html', id=user_id, gr=gr, lang=lang, questions=questindo)
    else:
        # Handle unexpected 'lang' value
        return "Error: Invalid language selection"

@app.route('/yes', methods=['GET', 'POST'])
def yes():
    if request.method == 'POST':
        form_data = dict(request.form)
        print(form_data)

        # Extract the necessary data from the form_data dictionary
        email = form_data.get('email')
        gr = form_data.get('gr')
        id = form_data.get('id')
        comments = form_data.get('comments')
        followup = form_data.get('followup')
        lang = form_data.get('lang')
        veteran = form_data.get('veteran')
        cryptorisk = form_data.get('cryptorisk')
        trustpower = form_data.get('trustpower')
        comments_a = form_data.get('comments_a')
        comments_b = form_data.get('comments_b')

        # Create a dictionary to map the question numbers to column names
        question_columns = {
            'question0': 'question0',
            'question1': 'question1',
            'question2': 'question2',
            'question3': 'question3',
            'question4': 'question4',
            'question5': 'question5',
            'question6': 'question6',
            'question7': 'question7',
            'question8': 'question8',
            'question9': 'question9',
            'question10' : 'question10',
            'question11': 'question11',
            'question12': 'question12',
            'question13': 'question13',
            'question14': 'question14',
            'question15': 'question15',
            'question16': 'question16',
            'question17': 'question17',
            'question18': 'question18',
            'question19': 'question19',
            'question20': 'question20',
            'question21': 'question21',
            'question22': 'question22',
            'question23': 'question23',
            'question24': 'question24',
            'question25': 'question25',
            'question26': 'question26',
            'question27': 'question27',
            'question28': 'question28',
            'question29': 'question29'
         }

        # Prepare the insert statement
        insert_values = {}
        for question_num, answer in form_data.items():
            if question_num in question_columns:
                column_name = question_columns[question_num]
                insert_values[column_name] = answer

        insert_values['email'] = email
        insert_values['gr'] = gr
        insert_values['id'] = id
        insert_values['comments'] = comments
        insert_values['followup'] = followup
        insert_values['lang'] = lang
        insert_values['veteran'] = veteran
        insert_values['cryptorisk'] = cryptorisk
        insert_values['trustpower'] = trustpower
        insert_values['comments_a'] = comments_a
        insert_values['comments_b'] = comments_b

        # Execute the insert statement
        with engine.connect() as conn:
            insert_statement = text("""
                INSERT INTO survey (question0, question1, question2, question3, question4, question5, question6, question7, question8, question9, question10,question11,question12, question13,question14,question15,question16,question17,question18,question19,question20,question21,question22,question23,question24,question25,question26,question27,question28,question29, email, gr, id, comments, followup, lang, veteran, cryptorisk, trustpower, comments_a, comments_b)
                VALUES (:question0, :question1, :question2,  :question3, :question4, :question5, :question6, :question7, :question8, :question9, :question10, :question11, :question12, :question13, :question14, :question15, :question16, :question17, :question18, :question19, :question20, :question21, :question22, :question23, :question24, :question25, :question26, :question27, :question28, :question29, :email, :gr, :id, :comments, :followup, :lang, :veteran, :cryptorisk, :trustpower, :comments_a, :comments_b)
            """)
            conn.execute(insert_statement, insert_values)

        # Return the appropriate template based on the lang value
        if lang == '1':
            return render_template('the_survey_ends-a.html')
        else:
            return render_template('the_survey_ends.html')
    return "Invalid request method"


if __name__ == "__main__":
  
  app.run(host="0.0.0.0", debug=True)