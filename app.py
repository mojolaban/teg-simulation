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
  if result == "1":
    return render_template('instruction-1.html')
  elif result == "2":
    return render_template('instruction-2.html')
  else:
    print("Error")
    
#----Insert initial game data from db to html
@app.route("/start")
def starting_game():
    init_data = fetch_init_data()
    return render_template('rounds.html', 
                           data=init_data)

     
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

  with engine.connect() as conn:
    conn.execute(text("INSERT INTO `teg-simulation`.`responses` (`sec`,`price`,`id`, `gr`, `pos`, `trx`) VALUES (:sec, :price, :id, :gr, :pos, :trx)"), {"sec": timer_value, "price": price_value, "id": user_id, "gr" : group_id, "pos" : pos_value, "trx" : trx_value})
    return jsonify({'message': 'Data successfully inserted'})
    print (trx_value)

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