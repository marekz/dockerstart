from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import requests
import subprocess
import json

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")

db = client.ImageRecognition
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
                "msg": "Invalid Username"
            }

            return jsonify(ret_json)

        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        users.insert({
            "Username": username,
            "Password": hashed_pw,
            "Tokens": 4
        })

        ret_json = {
            "status": 200,
            "msg": "You successfully signed up for this API"
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


def generate_return_dictonary(status, msg):
    ret_json = {
        "status": status,
        "msg": msg
    }

    return ret_json


def verify_credentials(username, password):
    if not user_exist(username):
        return generate_return_dictonary(301, "Invalid username"), True
    correct_pw = verify_pw(username, password)

    if not correct_pw:
        return generate_return_dictonary(302, "Invalid password"), True


class Classify(Resource):
    @staticmethod
    def post():
        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data["password"]
        url = posted_data["url"]

        ret_json = verify_credentials(username, password)
        error = verify_credentials(username, password)

        if error:
            return jsonify(ret_json)

        tokens = users.find({
            "Username": username
        })[0]["Tokens"]

        if tokens <= 0:
            return jsonify(generate_return_dictonary(300, "Not enought tokens!"))

        r = requests.get(url)

        ret_json = {}

        with open("temp.jpg", "wb") as f:
            f.write(r.content)
            proc = subprocess.Popen('python classify_image.py --model_dir=. --image_file=./temp.jpg', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
            proc.communicate()[0]
            proc.wait()
            with open("text.txt") as g:
                ret_json = json.load(g)

        users.update({
            "Username": username
        }, {
            "$set": {
                "Tokens": tokens - 1
            }
        })
        return ret_json


class Refill(Resource):
    def post(self):
        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data["admin_pw"]
        amount = posted_data["amount"]
        if not user_exist(username):
            return jsonify( generate_return_dictonary(301, "Invalid username"))

        correct_pw = "abc123"

        if not password == correct_pw:
            return jsonify( generate_return_dictonary(304, "Invalid administrator password"))

        users.update({
            "Username": username
        }, {
            "$set": {
                "Tokens": amount
            }
        })

        return jsonify( generate_return_dictonary(200, "Refilled successfully"))


api.add_resource(Register, '/register')
api.add_resource(Classify, '/classify')
api.add_resource(Refill, '/refill')

if __name__ == "__main__":
    app.run(host="0.0.0.0")
