from flask import Flask, redirect, render_template, request, jsonify, session, url_for
from database import engine, insert_group_treatment, fetch_init_data, retrieve_data
from sqlalchemy import text
from datetime import datetime
import json
import random

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/validate_passcode', methods=['POST'])
def validate_passcode():
    passcode = request.form.get('passcode')
    if len(passcode) == 6:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT passcode FROM passcodes WHERE passcode = :passcode;"), {"passcode": passcode})
            if result.fetchone():
                # Passcode exists, redirect to home.html
                return redirect(url_for('home'))
    # Passcode is invalid, show warning
    return render_template('index.html', warning=True)

@app.route('/home')
def home():
    return render_template('home.html')
  

#-----After home page, assign group and insert init data
@app.route("/instructions")
def after_instructions():
    result = insert_group_treatment()
    treatment_value = result['treatment']
    if treatment_value == 1:
        asset_type = 'stock'
        return render_template('instruction-1.html', id=result["id"], asset_type=asset_type)
    elif treatment_value == 2:
        asset_type = 'crypto'  
        return render_template('instruction-2.html', id=result["id"], asset_type=asset_type)
    else:
        return Error

#----Insert initial game data from db to try out instruction
@app.route("/tryout", methods=['POST'])
def tryout():
  id = request.form['id']
  print("ID:", id)  # Debug statement
  return render_template('instruction-tryout.html', id=id)
  
#----Insert initial game data from db to html
@app.route("/start", methods=['POST'])
def starting_game():
    id = request.form.get('id')
    print("ID:", id)  # Debug statement
    if id:
        init_data = fetch_init_data(id)
        print("Init Data:", init_data)  # Debug statement
        if init_data:
            return render_template('rounds.html', data=init_data)
    return "Error: Invalid ID"
       
#-----Start interacting with the data inside the game
#-----Send data to the database

@app.route("/sendData", methods=['POST'])
def send_games_data():
  data = request.get_json()
  timer_value = data.get('timerValue')
#  price_value = data.get('priceValue').replace(',', '')
  
  price_value = data.get('priceValue').replace(',', '')
  if not price_value:
      price_value = 0 
  
  user_id = data.get('userid').replace('\n', '').strip()
  group_id = data.get('groupid').replace('\n', '').strip()
  pos_value = data.get('posValue').replace('\n', '').strip()
  trx_value = data.get('trxValue')
  round_value = data.get('roundValue')
  crypto_prev_value = data.get('cryptoPrevValue').replace('\n', '').strip()
  fiat_prev_value = data.get('fiatPrevValue')
  crypto_value = data.get('cryptoValue')
  fiat_value = data.get('fiatValue')
  buy_prev_value = data.get('buyPrevValue')
  sell_value = data.get('sellValue')
  buy_value = data.get('buyValue')
  t_gain_value = data.get('tGainValue')
  t_tax_value = int(data.get('tTaxValue'))
  t_gain_net_value = data.get('tGainNetValue')
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
    conn.execute(text("INSERT INTO `teg-simulation`.`responses` (`sec`,`price`,`id`, `gr`, `pos`, `trx`, `round`, `crypto_prev`, `fiat_prev`,`crypto`, `fiat`, `buy_prev`, `buy`, `sell`, `t_gain`,`t_tax`, `t_gain_net`, `r_gain`, `r_gain_prev`, `r_tax`, `r_tax_prev`, `r_gain_net`, `tax_disclos`,`audit`) VALUES (:sec, :price, :id, :gr, :pos, :trx, :round, :crypto_prev, :fiat_prev, :crypto, :fiat, :buy_prev,:buy, :sell, :t_gain, :t_tax, :t_gain_net, :r_gain, :r_gain_prev, :r_tax, :r_tax_prev, :r_gain_net, :tax_disclos,:audit)"), {"sec": timer_value, "price": price_value, "id": user_id, "gr" : group_id, "pos" : pos_value, "trx" : trx_value, "round" : round_value, "crypto_prev" :crypto_prev_value,  "fiat_prev" :fiat_prev_value, "crypto" :crypto_value,  "fiat" :fiat_value, "buy_prev":buy_prev_value,"buy":buy_value, "sell":sell_value, "t_gain":t_gain_value, "t_tax":t_tax_value, "t_gain_net": t_gain_net_value, "r_gain": r_gain_value, "r_gain_prev": r_gain_prev_value, "r_tax": r_tax_value, "r_tax_prev": r_tax_prev_value,"r_gain_net": r_gain_net_value,"tax_disclos": tax_disclos_value,"audit": audit_value})
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

    result = conn.execute(text("SELECT round, gr, id, trx, crypto, fiat, buy, sell, pos, t_gain, r_gain, t_tax, crypto_prev, fiat_prev, buy_prev, r_tax, r_gain_net, t_gain_net, r_gain_prev, r_tax_prev, tax_disclos, tax_discre, audit, penalty, r_gain_final FROM responses WHERE id = :id ORDER BY ts DESC LIMIT 1;"), {"id": user_id})
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
                asset_type = "Stock"
            elif gr_value == '1':
                asset_type = "Crypto"
              
            if trx_value < 5:
                if pos_value == "s":
                    pos_value = "SELL"
                elif pos_value == "b":
                    pos_value = "BUY"
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
                "r_gain_final":r_gain_final
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
    return render_template('tax_reporting.html', summary_data=response_data)

#----Sending data from tax reporting page to db, then show them to audit page
@app.route("/tax_disclosure")
def tax_disclosure():
    data = request.args
    userid = data['id']
    taxdisclos = data['tax_disclos'].replace(',', '')
    audit_value = 0 if random.random() < 0.8 else 1
    print("Reported Data:")
    print(f"UserID: {userid}")
    print(f"Audit: {audit_value}")
    print(f"Tax Disclos: {taxdisclos}")

    with engine.connect() as conn:
        update_statement = text("""
            UPDATE `teg-simulation`.`responses`
            SET `tax_disclos` = :new_tax_disclos_value, `audit` = :audit_value
            WHERE `id` = :user_id
            ORDER BY `ts` DESC
            LIMIT 1
        """)
        conn.execute(
            update_statement,
            {"new_tax_disclos_value": taxdisclos, "audit_value": audit_value, "user_id": userid}
        )

        select_statement_1 = text("""
            SELECT `round`, `audit`
            FROM `teg-simulation`.`responses`
            WHERE `id` = :user_id
            ORDER BY `ts` DESC
            LIMIT 1
        """)
        result_1 = conn.execute(select_statement_1, {"user_id": userid})
        latest_round, latest_audit = result_1.fetchone()

        print("Latest Data:")
        print(f"Round: {latest_round}")
        print(f"Audit: {latest_audit}")

        if latest_audit == 1:
            response = retrieve_data(userid)
            response_data = response.json
            return render_template("tax_audit_1.html", summary_data=response_data)
        elif latest_audit == 0:
            response = retrieve_data(userid)
            response_data = response.json
            return render_template("tax_audit_0.html", summary_data=response_data)
 

#            select_statement_2 = text("""
#                SELECT `round`, `r_gain_final`
#                FROM `teg-simulation`.`responses`
#                WHERE `id` = :user_id AND `trx` = 5
#                ORDER BY `ts` DESC
#             """)
#            result_2 = conn.execute(select_statement_2, {"user_id": userid})
#            records = result_2.fetchall()


#            round_15, r_gain_final = result_2.fetchone()

#            if r_gain_final < 0:
#                r_gain_final = 100000

#            response_data = {
#                "round": round_15,
#                "r_gain_final": r_gain_final
#            }
          
#            response_data = []
#            for record in records:
#                round_15, r_gain_final = record
#                if r_gain_final < 0:
#                    r_gain_final = 100000
#                response_data.append({"round": round_15, "r_gain_final": r_gain_final})

#----Sending data from tax audit page to db, initiate new round then go to rounds
@app.route("/next_round") #, methods=["POST"])
def next_round():
    data = request.args
    userid = (data['id'])
    print("Next Round Data:")
    print(f"UserID: {userid}")

    with engine.connect() as conn:
        select_statement = text("""
            SELECT `round`, `gr` 
            FROM `teg-simulation`.`responses`
            WHERE `id` = :user_id
            ORDER BY `ts` DESC
            LIMIT 1
        """)
        result = conn.execute(select_statement, {"user_id": userid})
        latest_round, gr = result.fetchone()

        if latest_round < 15:
            next_round = latest_round + 1
            conn.execute(
                text("INSERT INTO `teg-simulation`.`responses`(`round`,`gr`, `id`, `trx`, `crypto`, `fiat`, `buy`, `sell`, `pos`, `t_gain`, `r_gain`, `t_tax`, `tax_disclos`, `audit`, `t_gain_net`, `r_gain_net`,`r_tax`,`sec`,`price`,`crypto_prev`, `fiat_prev`, `buy_prev`, `r_gain_prev`,`r_tax_prev`)VALUES (:round, :gr, :id, '0', '1.00', '0', '0', '0','s','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0')"),
                {"round": next_round, "gr": gr, "id": userid}
            )
            init_data = fetch_init_data({userid})
        #       print("Init Data:", init_data)  # Debug statement
            if init_data:
                return render_template('rounds.html', data=init_data)      
        else:
            random_number = random.randint(1, 15)

            select_statement_2 = text("""
                SELECT `id`, `gr`,`round`, CASE WHEN `r_gain_final` <= 0 THEN 100000 ELSE `r_gain_final` END AS `r_gain_final`
                FROM `teg-simulation`.`responses`
                WHERE `id` = :user_id AND `round` = :random_number
                ORDER BY `trx` DESC
                LIMIT 1
            """)
            result_2 = conn.execute(select_statement_2, {"user_id": userid, "random_number": random_number})
            result = result_2.fetchone()

            # Check if the result is None
            if result is None:
                # Handle the case when no data is found
                print("No data found in select_statement_2")
                return "No data found"

            user_id, gr, comp_round, comp_amt = result
            comp_rgainfinal = comp_amt
            comp_amt = comp_amt * 0.0002

            print("Compensation:")
            print(f"UserID: {user_id}")
            print(f"Group: {gr}")
            print(f"Round: {comp_round}")
            print(f"Round Gain Amount: {comp_rgainfinal}")
            print(f"Compensation Amount: {comp_amt}")

            return render_template("the_random_picker.html", user_id=user_id, comp_round=comp_round, comp_amt=comp_amt, comp_rgainfinal=comp_rgainfinal, gr=gr)





@app.route('/survey', methods=['GET', 'POST'])
def survey():
    comp_amt = request.form.get('comp_amt')
    comp_round = request.form.get('comp_round')
    comp_rgainfinal = request.form.get('comp_rgainfinal')
    user_id = request.form.get('user_id')
    gr = str(request.form.get('gr')).replace('\n', '').strip()[:1]


    # Process the data as needed
    with engine.connect() as conn:
      insert_statement = text("""
          INSERT INTO compensation (comp_amt, id, comp_round, comp_rgainfinal, gr)
          VALUES (:comp_amt, :user_id, :comp_round,  :comp_rgainfinal, :gr)
      """)
      conn.execute(
          insert_statement,
          {"comp_amt": comp_amt, "user_id": user_id, "comp_round": comp_round,  "comp_rgainfinal": comp_rgainfinal, "gr": gr}
      )

    print("Recorded compensation:")
    print(f"UserID: {user_id}")
    print(f"Group: {gr}")
    print(f"CompAmt: {comp_amt}")
    print(f"CompRound: {comp_round}")
    print(f"CompRoundGain: {comp_rgainfinal}")

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
        'I trust the tax officers because the tax officers pursue important goals.',        
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

    return render_template('the_survey.html', id=user_id, gr=gr, questions=questions)

@app.route('/yes', methods=['GET', 'POST'])
def yes():
    if request.method == 'POST':
        form_data = dict(request.form)
        print(form_data)

        # Extract the necessary data from the form_data dictionary
        email = form_data.get('email')
        gr = form_data.get('gr')
        id = form_data.get('id')

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

        # Execute the insert statement
        with engine.connect() as conn:
            insert_statement = text("""
                INSERT INTO survey (question0, question1, question2, question3, question4, question5, question6, question7, question8, question9, question10,question11,question12, question13,question14,question15,question16,question17,question18,question19,question20,question21,question22,question23,question24,question25,question26,question27,question28,question29, email, gr, id)
                VALUES (:question0, :question1, :question2,  :question3, :question4, :question5, :question6, :question7, :question8, :question9, :question10, :question11, :question12, :question13, :question14, :question15, :question16, :question17, :question18, :question19, :question20, :question21, :question22, :question23, :question24, :question25, :question26, :question27, :question28, :question29, :email, :gr, :id)
            """)
            conn.execute(insert_statement, insert_values)

        return "Thank you for participating!"
    return "Invalid request method"


if __name__ == "__main__":
  
  app.run(host="0.0.0.0", debug=True)