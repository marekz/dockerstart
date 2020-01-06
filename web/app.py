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
