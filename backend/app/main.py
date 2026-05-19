from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для всех доменов

# Фиктивные данные
users = [
    {"id": 1, "name": "Chelsey Dietrich", "email": "Chelsey@example.com", "phone": "2421526363446", "company_name": "apple"},
    {"id": 2, "name": "Clementina DuBuque", "email": "Clementina@example.com", "phone": "2353464856", "company_name": "google"},
    {"id": 3, "name": "Glenna Reichert", "email": "Glenna@example.com", "phone": "9786078956", "company_name": "microsoft"}
]

@app.route('/')
def root():
    return jsonify({"message": "API работает!", "users_count": len(users)})

@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(users)

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    for user in users:
        if user['id'] == user_id:
            return jsonify(user)
    return jsonify({"error": "Пользователь не найден"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)