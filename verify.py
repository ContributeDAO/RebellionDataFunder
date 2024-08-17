
"""
A module that provide encrypted port verification.
"""
from flask import Flask, jsonify,request,Response
import os
import base64
from typing import List, Dict
import uuid

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
