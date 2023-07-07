from flask import Flask, render_template, request, jsonify
from database import engine, insert_group_treatment
from sqlalchemy import text

app = Flask(__name__)

@app.route("/")
def hello_world():
  return render_template('home.html')
  
@app.route("/instructions")
def instruction_group():
  result = insert_group_treatment()
  if result == "1":
    return render_template('treat1.html')
  elif result == "2":
    return render_template('treat2.html')
  else:
    return render_template('error.html')




if __name__ == "__main__":
  app.run(host="0.0.0.0", debug=True)