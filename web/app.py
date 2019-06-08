from flask import Flask, jsonify, request

from pymongo import MongoClient

app = Flask(__name__)

@app.route('/')
def hello_world():
    return "Hello World!"

@app.route('/hithere')
def hi_there_everyone():
    return "I just hit /hithere"

@app.route('/add_two_nums', methods=["POST"])
def add_two_nums():
    dataDict = request.get_json()

    if "y" not in dataDict:
        return "ERROR", 305
        
    x = dataDict["x"]
    y = dataDict["y"]

    z = x+y
    retJSON = {
        "z": z
    }
    return jsonify(retJSON), 200

@app.route('/bye')
def bye():
    retJson = {
        'Name':'MarekZ',
        'Age':22,
        "phones":[
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
    return jsonify(retJson)

if __name__=="__main__":
    app.run(debug=True)