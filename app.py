from flask import Flask, render_template, request, jsonify
from database import engine, insert_group_treatment, fetch_init_data
from sqlalchemy import text
from datetime import datetime

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
@app.route("/start", methods=["POST"])
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
@app.route("/sendData", methods=['POST'])
def send_games_data():
  data = request.get_json()
  timer_value = data.get('timerValue')
  price_value = data.get('priceValue').replace(',', '')  
  user_id = data.get('userid').replace('\n', '').strip()
  group_id = data.get('groupid').replace('\n', '').strip()
  pos_value = data.get('posValue').replace('\n', '').strip()
  trx_value = data.get('trxValue')
  round_value = data.get('roundValue')
  crypto_prev_value = data.get('cryptoPrevValue').replace('\n', '').strip()
  fiat_prev_value = data.get('fiatPrevValue').replace('\n', '').strip()
  crypto_value = data.get('cryptoValue')
  fiat_value = data.get('fiatValue')
  buy_prev_value = data.get('buyPrevValue').replace(',', '')
  sell_value = data.get('sellValue')
  buy_value = data.get('buyValue').replace(',', '')
  t_gain_value = data.get('tGainValue')
  t_tax_value = data.get('tTaxValue')
  t_gain_net_value = data.get('tGainNetValue')
  r_gain_value = data.get('rGainValue')
  r_gain_prev_value = data.get('rGainPrevValue')
  r_tax_value = data.get('rTaxValue')
  r_tax_prev_value = data.get('rTaxPrevValue')
  r_gain_net_value = data.get('rGainNetValue')
  tax_discre_value = data.get('taxDiscreValue')
  tax_disclos_value =data.get('taxDisclosValue')
  audit_value =data.get('auditValue')
  penalty_value =data.get('penaltyValue')
  r_gain_final_value =data.get('rGainFinalValue')
  

  with engine.connect() as conn:
    conn.execute(text("INSERT INTO `teg-simulation`.`responses` (`sec`,`price`,`id`, `gr`, `pos`, `trx`, `round`, `crypto_prev`, `fiat_prev`,`crypto`, `fiat`, `buy_prev`, `buy`, `sell`, `t_gain`,`t_tax`, `t_gain_net`, `r_gain`, `r_gain_prev`,`r_tax`,`r_tax_prev`,`r_gain_net`,`tax_discre`,`tax_disclos`,`audit`,`penalty`,`r_gain_final`) VALUES (:sec, :price, :id, :gr, :pos, :trx, :round, :crypto_prev, :fiat_prev, :crypto, :fiat, :buy_prev,:buy, :sell, :t_gain, :t_tax, :t_gain_net, :r_gain, :r_gain_prev, :r_tax, :r_tax_prev,:r_gain_net,:tax_discre,:tax_disclos,:audit,:penalty,:r_gain_final)"), {"sec": timer_value, "price": price_value, "id": user_id, "gr" : group_id, "pos" : pos_value, "trx" : trx_value, "round" : round_value, "crypto_prev" :crypto_prev_value,  "fiat_prev" :fiat_prev_value, "crypto" :crypto_value,  "fiat" :fiat_value, "buy_prev":buy_prev_value,"buy":buy_value, "sell":sell_value, "t_gain":t_gain_value, "t_tax":t_tax_value, "t_gain_net": t_gain_net_value, "r_gain": r_gain_value, "r_gain_prev": r_gain_prev_value, "r_tax": r_tax_value, "r_tax_prev": r_tax_prev_value,"r_gain_net": r_gain_net_value,"tax_discre": tax_discre_value,"tax_disclos": tax_disclos_value,"audit": audit_value,"penalty": penalty_value,"r_gain_final": r_gain_final_value,})

#"t_tax": t_tax_value, "t_gain_net": t_gain_net_value
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
    print(f"Fiat Prev Value: {fiat_prev_value}")
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
    print(f"Tax Discre Value: {tax_discre_value}")
    print(f"Audit Value: {audit_value}")
    print(f"Penalty Value: {penalty_value}")
    print(f"Rnd Gain Final Value: {r_gain_final_value}")
    
#    print(t_tax_value)
#    print(t_gain_net_value)
    return jsonify({'message': 'Data successfully inserted'})
    #return render_template('rounds.html', data=update_data)


#  round_value = data.get('roundValue').replace('\n', '').strip()
 # gr_value = data.get('grValue').replace('\n', '').strip()
#    conn.execute(text("INSERT INTO `teg-simulation`.`core` (`sec`,`price`,`id`) VALUES (:sec, :price, :id)"), {"sec": #timer_value, "price": price_value, "id": user_id})
#    return jsonify({'message': 'Data successfully inserted'})
#update current data with second and price
 #   conn.execute(
 #     text("UPDATE `teg-simulation`.`responses` SET `sec` = :sec, `price` = :price WHERE `id` = :id"),
 #     {"id": user_id, "sec": timer_value, "price": price_value})
#    conn.execute(
#    text("UPDATE `teg-simulation`.`responses` SET `sec` = :sec, `price` = :price WHERE `id` = :id AND `ts` = (SELECT MAX(`ts`) FROM `teg-simulation`.`responses` WHERE `id` = :id)"),
#    {"id": user_id, "sec": timer_value, "price": price_value})

#send the to the next records:
#    conn.execute(text("INSERT INTO `teg-simulation`.`responses` (`round`) VALUES (:round)"), {"round": round_value})


    
# Insert the latest 'gr', 'id' into the 'log' table
#  timer_value = data.get('timerValue')
#  price_value = data.get('priceValue').replace(',', '')  # Remove commas from priceValue
#  user_id = data.get('user_id')  # Assign the user_id from the request payload    


if __name__ == "__main__":
  app.run(host="0.0.0.0", debug=True)