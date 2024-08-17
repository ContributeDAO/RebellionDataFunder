from flask import Flask, jsonify,request,Response
import os
import verify
from typing import List, Dict

#import logging
app = Flask(__name__)
 

@app.route('/')
def index():
    return "Welcome, this is a Flask app deployed on Zeabur"
 

@app.route('/keys/', methods=['POST'])
def handle_keys():
    try:
        key_info = request.json
        key_id = key_info.get('key_id')
        key_base64 = key_info.get('key')

        if key_id is None or key_base64 is None:
            return jsonify({"error": "Missing key_id or key"}), 400

        # 将 Base64 编码的字符串转回 bytes
        key = base64.b64decode(key_base64)
        print(f"Received key ID: {key_id}")
        print(f"Received key: {key}")
        session_id = generate_session_id()
        new_verifier = Verifier(session_id, key)
        #检测是否已经存在相同的验证者
        existing_verifier =  next((v['verifier'] for v in verifiers.values()  if v['verifier'].public_key == new_verifier.public_key), None)
        if existing_verifier:
            print(f"Verifier with public key {base64.b64encode(key).decode()} already exists.")
            if existing_verifier.verification_requests:
                # 如果有未处理的请求，返回第一个请求的信息
                pending_request = existing_verifier.verification_requests[0]
                return jsonify({
                    "message": "Verifier already exists with pending requests",
                    "pending_request": pending_request.to_json()
                }), 200
                    
            return jsonify({"message": "Key have mark"}), 201


        
        else:
            # 将新的验证者添加到字典中
            verifier_id = f"verifier{len(verifiers) + 1}"
            verifiers[len(verifiers)] = {"id": verifier_id, "verifier": new_verifier}
        
            print(f"Generated session ID: {session_id}")
            print(f"Received key ID: {key_id}")        
            # 这里可以添加将密钥保存到数据库或文件的代码
            return jsonify({"message": "Key received successfully"}), 201

    except Exception as e:
        print(f"Error in handle_keys: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/verify_signature/', methods=['POST'])
def handle_verify_signature():
    data = request.json
    public_key = base64.b64decode(data.get('public_key'))
    verifier_hash = base64.b64decode(data.get('verifier_hash'))
    hash_signature = base64.b64decode(data.get('hash_signature'))
    # 使用 verifier_hash 选择验证者
    selected_verifier = select_verifier(verifier_hash)["verifier"]
    
    # 创建签名验证请求
    verification_request = create_verification_request(public_key, selected_verifier.public_key,verifier_hash, hash_signature)
    selected_verifier.add_verification_request(verification_request)
    # 在实际应用中，你可能会将这个请求发送到另一个服务或队列中进行处理
    # 这里我们只是返回创建的请求
    return Response(verification_request.to_json(), mimetype='application/json'), 202  # 202 Accepted    


@app.route('/verify_result/', methods=['POST'])
def handle_verify_result():
    data = request.json
    request_id=data.get('request_id')
    #verifier_public_key = base64.b64decode(data.get('request_public_key'))
    
    # verifier_hash = base64.b64decode(data.get('verifier_hash'))
    # hash_signature = base64.b64decode(data.get('hash_signature'))
    verification_status=data.get('verification_status')
        # 遍历 verifiers 字典，查找匹配的 request_id
    for verifier in verifiers.values():
        # 遍历每个 verifier 的 verification_requests 列表
        for verification_request in verifier["verifier"].verification_requests:
            if verification_request.request_id == request_id:
                # 更新找到的 VerificationRequest

                verification_request.verification_status= verification_status

                return jsonify({"message": "Verification result updated successfully"}), 250

    # 如果没有找到匹配的 request_id
    return jsonify({"error": "Verification request not found"}), 404


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000), host='0.0.0.0')