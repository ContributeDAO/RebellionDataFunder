from flask import Flask, jsonify,request,Response
import os
import base64
from typing import List, Dict
import uuid
import json
#import logging
app = Flask(__name__)
 
 
class VerificationRequest:
    def __init__(self,request_id, request_public_key, verifier_public_key, verification_hash, hash_signature,verification_status):
        self.request_id=request_id
        self.verifier_public_key = verifier_public_key
        self.request_public_key = request_public_key
        self.verification_hash = verification_hash
        self.hash_signature = hash_signature
        self.verification_status = verification_status
        
    def verify(self) -> bool:
        # 这里应该实现实际的验证逻辑
        # 为了演示，我们假设验证总是成功
        self.verification_status = True
        return self.verification_status
    
    def to_json(self):
        return json.dumps({
            'request_id': self.request_id,
            'verifier_public_key': base64.b64encode(self.verifier_public_key).decode('utf-8'),
            'request_public_key': base64.b64encode(self.request_public_key).decode('utf-8'),
            'verification_hash': base64.b64encode(self.verification_hash).decode('utf-8'),
            'hash_signature': base64.b64encode(self.hash_signature).decode('utf-8'),
            'verification_status': self.verification_status
        })

    @classmethod
    def from_json(cls, json_str):
        # 如果 json_data 已经是一个字典，直接使用它
        if isinstance(json_data, dict):
            data = json_data
        else:
            # 否则，假设它是一个 JSON 字符串，并解析它
            data = json.loads(json_data)
        return cls(
            request_id=data['request_id'],
            request_public_key=base64.b64decode(data['request_public_key']),
            verifier_public_key=base64.b64decode(data['verifier_public_key']),
            verification_hash=base64.b64decode(data['verification_hash']),
            hash_signature=base64.b64decode(data['hash_signature']),
            verification_status=data['verification_status']
        )
 
 
class Verifier:
    def __init__(self, session_id: str, public_key: str):
        self.session_id = session_id
        self.public_key = public_key
        self.verification_requests: List[VerificationRequest] = []
        self.is_verified = False

    def add_verification_request(self, request: VerificationRequest):
        self.verification_requests.append(request)

    def verify(self) -> bool:
        # 这里应该实现实际的验证逻辑
        # 为了演示，我们假设如果有任何验证请求，就认为验证成功
        self.is_verified = len(self.verification_requests) > 0
        return self.is_verified
    
    def __eq__(self, other):
        if isinstance(other, Verifier):
            return self.public_key == other.public_key
        return False    
 
 # 用于存储验证者的字典
 
verifiers = {}

def generate_session_id():
    return str(uuid.uuid4())

def select_verifier(verifier_hash):
    # 使用 verifier_hash 来确定性地选择一个验证者
    hash_int = int.from_bytes(verifier_hash, byteorder='big')
    index = hash_int % len(verifiers)
    return list(verifiers.values())[index]

def create_verification_request(request_public_key,selected_verifier_public_key,verification_hash, hash_signature):
    return VerificationRequest(str(os.urandom(16)),request_public_key,selected_verifier_public_key,verification_hash,hash_signature,'pending')



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