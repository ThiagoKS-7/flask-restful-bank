'''
Registrar user 0 tokens
Cada user recebe 10 tokens
post de classification - 1 token
'''
from flask import Flask,render_template
from flask_restful import Api 
from models.resources.manage_bank import Register,Transfer,Balance, TakeLoan, PayLoan, GetUsers,Refill

app = Flask(__name__)
api =  Api(app)
 
title = "Flask tutorial"
subtitle = "Running on port 5000"


'''
***********************
  *       API ROUTES    *
  ***********************
'''
api.add_resource(Register, '/register')
api.add_resource(Transfer, '/transfer')
api.add_resource(Balance, '/balance')
api.add_resource(TakeLoan, '/take-loan')
api.add_resource(PayLoan, '/pay-loan')
api.add_resource(GetUsers, '/get-users')
api.add_resource(Refill, '/refill')

'''
***********************
*       APP ROUTES    *
***********************
'''
@app.route('/')
def hello_world():
  return render_template('index.html', title=title, subtitle=subtitle)
@app.route('/teste')
def test():
  return render_template('test.html')

if __name__ == '__main__':
  app.run(host='0.0.0.0')

