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
    })[0]["password"]

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
    if not user_exist(username, password):
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
