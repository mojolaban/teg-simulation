from flask import Flask, render_template, request, jsonify, session
from database import engine, insert_group_treatment, fetch_init_data, retrieve_data
from sqlalchemy import text
from datetime import datetime
import json
import random

app = Flask(__name__)

@app.route("/")
def hello_world():
  return render_template('home.html')

#-----After Instruction page, assign group and insert init data
@app.route("/instructions")
def after_instructions():
    result = insert_group_treatment()
    treatment_value = result['treatment']
    if treatment_value == 1:
        return render_template('instruction-1.html', id=result["id"])
    elif treatment_value == 2:
        return render_template('instruction-2.html', id=result["id"])
    else:
        return Error

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
@app.route("/tax_disclosure") #, methods=["POST"]
def tax_disclosure():
  
    data = request.args
    userid = (data['id'])
    taxdisclos = (data['tax_disclos']).replace(',', '')
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
      conn.execute(update_statement, {"new_tax_disclos_value": taxdisclos, "audit_value": audit_value, "user_id": userid})
      
      select_statement = text("""
        SELECT `round`, `audit`
        FROM `teg-simulation`.`responses`
        WHERE `id` = :user_id
        ORDER BY `ts` DESC
        LIMIT 1
        """)
      result = conn.execute(select_statement, {"user_id": userid})
      latest_round, latest_audit = result.fetchone()
        
    print("Latest Data:")
    print(f"Round: {latest_round}")
    print(f"Audit: {latest_audit}")
 
    if latest_round < 15:
        if latest_audit == 1:
            response = retrieve_data(userid)
            response_data =  response.json 
            return render_template("tax_audit_1.html", summary_data=response_data)
        elif latest_audit == 0:
            response = retrieve_data(userid)
            response_data =  response.json 
            return render_template("tax_audit_0.html", summary_data=response_data)
    return jsonify(data)


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

        if latest_round is not None:
            next_round = latest_round + 1
        else:
            next_round = 1

        conn.execute(
            text("INSERT INTO `teg-simulation`.`responses`(`round`,`gr`, `id`, `trx`, `crypto`, `fiat`, `buy`, `sell`, `pos`, `t_gain`, `r_gain`, `t_tax`, `tax_disclos`, `audit`, `t_gain_net`, `r_gain_net`,`r_tax`,`sec`,`price`,`crypto_prev`, `fiat_prev`, `buy_prev`, `r_gain_prev`,`r_tax_prev`)VALUES (:round, :gr, :id, '0', '1.00', '0', '0', '0','s','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0')"),
            {"round": next_round, "gr": gr, "id": userid}
        )
    init_data = fetch_init_data({userid})
#       print("Init Data:", init_data)  # Debug statement
    if init_data:
        return render_template('rounds.html', data=init_data)

  
if __name__ == "__main__":
  app.run(host="0.0.0.0", debug=True)