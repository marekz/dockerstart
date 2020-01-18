from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.BankAPI
users = db["Users"]


def user_exist(username):
    if users.find({"Username": username}).count() == 0:
        return False
    else:
        return True


class Register(Resource):
    def post(self):
        posted_data = request.get_json()
        
        username = posted_data["username"]
        password = posted_data["password"]
        
        if user_exist(username):
            ret_json = {
                "status": 301,
                "msg": "Invalid username"
            }
            return jsonify(ret_json)

        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        users.insert({
            "Username": username,
            "Password": hashed_pw,
            "Own": 0,
            "Debt": 0
        })

        ret_json = {
            "status": 200,
            "msg": "You successfully signed up for the API"
        }

        return jsonify(ret_json)


def verify_pw(username, password):
    if not user_exist(username):
        return False

    hashed_pw = users.find({
        "Username": username
    })[0]["Password"]

    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False


def cash_with_user(username):
    cash = users.find({
        "Username": username
    })[0]["Own"]

    return cash


def debt_with_user(username):
    debt = users.find({
        "Username": username
    })[0]["Debt"]

    return debt


def generate_return_dictionary(status, msg):
    ret_json = {
        "status": status,
        "msh": msg
    }

    return ret_json


# ErrorDictionary, True/False
def verify_credentials(username, password):
    if not user_exist(username):
        return generate_return_dictionary(301, "Invalid username"), True

    correct_pw = verify_pw(username, password)

    if not correct_pw:
        return generate_return_dictionary(302, "Incorrect password"), True

    return None, False


def update_account(username, balance):
    users.update({
        "Username": username
    }, {
        "$set": {
            "Own": balance
        }
    })


def update_debt(username, balance):
    users.update({
        "Username": username
    }, {
        "$set": {
            "Debt": balance
        }
    })


class Add(Resource):
    def post(self):
        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data["password"]
        money = posted_data["amount"]

        ret_json, error = verify_credentials(username, password)

        if error:
            return jsonify(ret_json)

        if money <= 0:
            return jsonify(generate_return_dictionary(304, "The money amount entered must be > 0"))

        cash = cash_with_user(username)
        money -= 1
        bank_cash = cash_with_user(username)

        update_account("BANK", bank_cash + 1)

        update_account(username, cash + money)

        return jsonify(generate_return_dictionary(200, "Amount added successfully to account"))


class Transfer(Resource):
    def post(self):
        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data["password"]
        to = posted_data["to"]
        money = posted_data["amount"]

        ret_json, error = verify_credentials(username, password)

        if error:
            return jsonify(ret_json)

        cash = cash_with_user(username)

        if cash <= 0:
            return jsonify(generate_return_dictionary(304, "You're out of money, please add or take a loan"))

        if not user_exist(to):
            return jsonify(generate_return_dictionary(301, "Reciever username is invalid"))

        cash_from = cash_with_user(username)
        cash_to = cash_with_user(username)
        bank_cash = cash_with_user("BANK")

        update_account("BANK", bank_cash + 1)
        update_account(to, cash_to + money - 1)
        update_account(username, cash_from - money)

        return jsonify(generate_return_dictionary(200, "Amount transfered successfully"))


class Balance(Resource):
    def post(self):

        posted_date = request.get_json()
        username = posted_date["username"]
        password = posted_date["password"]

        ret_json, error = verify_credentials(username, password)

        if error:
            return jsonify(ret_json)

        ret_json = users.find({
            "Username": username,
        }, {
            "Password": 0,
            "_id": 0
        })[0]

        return jsonify(ret_json)


class TakeLoan(Resource):
    def post(self):
        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data["password"]
        money = posted_data["amount"]

        ret_json, error = verify_credentials(username, password)

        if error:
            return jsonify(ret_json)

        cash = cash_with_user(username)
        debt = cash_with_user(username)
        update_account(username, cash + money)
        update_debt(username, debt + money)

        return jsonify(generate_return_dictionary(200, "Loan added to your account"))


class PayLoan(Resource):
    def post(self):
        posted_date = request.get_json()
        username = posted_date["username"]
        password = posted_date["password"]
        money = posted_date["amount"]

        ret_json, error = verify_credentials(username, password)

        if error:
            return jsonify(ret_json)

        cash = cash_with_user(username)

        if cash < money:
            jsonify(generate_return_dictionary(303, "Not enough cash in your account"))

        debt = debt_with_user(username)
        update_account(username, cash - money)
        update_debt(username, debt - money)

        return jsonify(generate_return_dictionary(200, "You've successfully paid your loan"))


api.add_resource(Register, '/register')
api.add_resource(Add, '/add')
api.add_resource(Transfer, '/transfer')
api.add_resource(Balance, '/balance')
api.add_resource(TakeLoan, '/take_loan')
api.add_resource(PayLoan, '/pay_loan')


if __name__ == "__main__":
    app.run(host='0.0.0.0')


