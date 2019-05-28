from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/')
def hello_world():
    return "Hello World!"

@app.route('/hithere')
def hi_there_everyone():
    return "I just hit /hithere"

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
    # app.run(host="127.0.0.1", port=80)
    app.run(debug=True)