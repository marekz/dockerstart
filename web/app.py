"""
Registration of a user 0 tokens
Each user gets 10 tokens
Store a sentence on our database for 1 token
Retrive his stored sentence on out database for 1 token
"""
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.SemtencesDatabase
users = db["users"] 

class Register(Resource):
    def post(self):
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["password"]

        print(password)

        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        #store username and password into database
        users.insert({
            "Username": username,
            "Password": hashed_pw,
            "Sentence": "",
            "Tokens": 6
        })

        retJson = {
            "status": 200,
            "msg": "You successully signed up for API"
        }

        return jsonify(retJson)


def verifyPw(username, password):
    hashed_pw = users.find({
        "Username": username
    })[0]['Password']

    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False


def countTokens(username):
    tokens = users.find({
        "Username": username
    })[0]["Tokens"]
    return tokens


class Store(Resource):
    def post(self):
        #Step 1 get the posted data
        postedData = request.get_json()

        #Step 2 os to read the data
        username = postedData["username"]
        password = postedData["password"]
        sentence = postedData["sentence"]

        #Step 3 verify the username pw match
        correct_pw = verifyPw(username, password)

        if not correct_pw:
            retJson = {
                "status": 302
            }
            return jsonify(retJson)

        #step 4 Verivy user has enough tokens
        num_tokens = countTokens(username)

        if num_tokens <= 0:
             retJson = {
                 "status": 301
             }
             return jsonify(retJson)

        #step 5 store the sentence, take one token away and return 200OK
        users.update({
            "Username": username
            }, {
                "$set": {
                    "Sentence": sentence, 
                    "Tokens": num_tokens-1
                    }
            })

        retJson = {
            "status": 200,
            "msg": "Sentence saved successfully"
        }
        
        return jsonify(retJson)


class Get(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]

        correct_pw = verifyPw(username, password)

        if not correct_pw:
            retJson = {
                "status": 302
            }
            return jsonify(retJson)

        num_tokens = countTokens(username)

        if num_tokens <= 0:
            retJson = {
                "status": 301
            }
            return jsonify(retJson)

        #Make the user pay
        users.update({
            "Username": username
        }, {
            "$set": {
                "Tokens": num_tokens-1
            }
        })

        sentence = users.find({
            "Username": username
        })[0]["Sentence"]

        retJson = {
            "status": 200,
            "sentence": sentence
        }

        return jsonify(retJson)



api.add_resource(Register, '/register')
api.add_resource(Store, '/store')
api.add_resource(Get, '/get')


if __name__ == "__main__":
    app.run(host='0.0.0.0')






"""

from flask import Flask, jsonify, request
from flask_restful import Api, Resource

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
# try:
#     client.admin.command('ismaster')
# except ConnectionFailure:
#     print("Server not available")

db = client.aNewDB
# print(db.test.count_documents({'x': 1})
UserNum = db["UserNum"]
UserNum.insert({
    'num_of_users': 0
})


class Visit(Resource):
    def get(self):
        prev_num = UserNum.find({})[0]['num_of_users']
        new_num = prev_num + 1
        UserNum.update({}, {"$set":{"num_of_users": new_num}})
        return str("Hello user " + str(new_num))
        # return str("Hello user " + str(1))


def check_posted_data(posted_data, function_name):
    if function_name == "add" or function_name == "subtract" or function_name == "multiply":
        if "x" not in posted_data or "y" not in posted_data:
            return 301
        else:
            return 200

    elif function_name == "division":
        if "x" not in posted_data or "y" not in posted_data:
            return 301
        elif int(posted_data["y"]) == 0:
            return 302
        else:
            return 200


class Add(Resource):
    def post(self):
        posted_data = request.get_json()

        status_code = check_posted_data(posted_data, "add")

        if status_code != 200:
            ret_json = {
                "Message": "An error happen",
                "Status Code": status_code
            }

            return jsonify(ret_json)

        x = posted_data["x"]
        print("x: " + str(x))
        y = posted_data["y"]
        print("y: " + str(y))
        x = int(x)
        y = int(y)
        ret = x + y
        print(ret)
        ret_map = {
            'Message': ret,
            'Status code': 200
        }
        return jsonify(ret_map)


class Subtract(Resource):
    def post(self):
        posted_data = request.get_json()

        status_code = check_posted_data(posted_data, "subtract")

        if status_code != 200:
            ret_json = {
                "Message": "An error happen",
                "Status Code": status_code
            }

            return jsonify(ret_json)

        x = posted_data["x"]
        y = posted_data["y"]
        x = int(x)
        y = int(y)
        ret = x - y
        ret_map = {
            'Message': ret,
            'Status code': 200
        }
        return jsonify(ret_map)


class Multiply(Resource):
    def post(self):
        posted_data = request.get_json()

        status_code = check_posted_data(posted_data, "multiply")

        if status_code != 200:
            ret_json = {
                "Message": "An error happened",
                "Status Code": status_code
            }

            return jsonify(ret_json)

        x = posted_data["x"]
        y = posted_data["y"]
        x = int(x)
        y = int(y)
        ret = x * y
        ret_map = {
            'Message': ret,
            'Status code': 200
        }
        return jsonify(ret_map)


class Divide(Resource):
    def post(self):
        posted_data = request.get_json()

        status_code = check_posted_data(posted_data, "division")

        if status_code != 200:
            ret_json = {
                "Message": "An error happend",
                "Status Code": status_code
            }

            return jsonify(ret_json)

        x = posted_data["x"]
        y = posted_data["y"]
        x = int(x)
        y = int(y)
        ret = x / y
        print(ret)
        ret_map = {
            'Message': ret,
            'Status code': 200
        }
        return jsonify(ret_map)


api.add_resource(Add, '/add')
api.add_resource(Subtract, '/subtract')
api.add_resource(Multiply, '/multiply')
api.add_resource(Divide, '/divide')
api.add_resource(Visit, '/hello')


@app.route('/')
def hello_world():
    return "Hello World!"


@app.route('/hithere')
def hi_there_everyone():
    return "I just hit /hithere"


@app.route('/add_two_nums', methods=["POST"])
def add_two_nums():
    data_dict = request.get_json()

    if "y" not in data_dict:
        return "ERROR", 305

    x = data_dict["x"]
    y = data_dict["y"]

    z = x + y
    ret_json = {
        "z": z
    }
    return jsonify(ret_json), 200


@app.route('/bye')
def bye():
    ret_json = {
        'Name': 'MarekZ',
        'Age': 22,
        "phones": [
            {
                "phoneName": "Samsung",
                "phoneNumber": 11111111
            },
            {
                "phoneName": "Nokia",
                "phoneNumber": 11112111
            }
        ]
    }
    return jsonify(ret_json)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
    # app.run(debug=True)

"""