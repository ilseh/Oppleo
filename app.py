from flask import Flask, make_response, jsonify

app = Flask(__name__)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/')
def index():
    return "Service for charging electric cars"


@app.route('/charging/<string:rfid>', methods=['POST'])
def start_charging(rfid):
    # verify if rfid is valid (known)
    # create new charging session (in db)
    # return sessionid
    return jsonify({'session_id': 1})


if __name__ == '__main__':
    app.run(debug=True)
