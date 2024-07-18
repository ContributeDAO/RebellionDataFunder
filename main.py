from flask import Flask
import os
import jsonify
import request
 
app = Flask(__name__)
 
@app.route('/')
def index():
    return "Welcome, this is a Flask app deployed on Zeabur"
 
@app.route('/items/', methods=['POST'])
def handle_items():
    item = request.json
    return jsonify(item), 201

@app.route('/keys/', methods=['POST'])
def handle_keys():
    key_info = request.json
    key_id = key_info.get('key_id')
    key = key_info.get('key')

    if key_id is None or key is None:
        return jsonify({"error": "Missing key_id or key"}), 400

    print(f"Received key ID: {key_id}")
    print(f"Received key: {key}")

    # 这里可以添加将密钥保存到数据库或文件的代码

    return jsonify({"message": "Key received successfully"}), 201


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000), host='0.0.0.0')