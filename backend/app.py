from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Разрешаем запросы с любого фронтенда

@app.route('/api/ping', methods=['GET'])
def ping():
    return jsonify({
        "status": "success",
        "message": "Backend is online!",
        "data": None
    })
@app.route("/")
def root():
    return "Backend is running"


if __name__ == '__main__':
    app.run(debug=True, port=5000)
