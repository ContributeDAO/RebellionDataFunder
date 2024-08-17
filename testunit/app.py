from flask import Flask, jsonify, redirect, request, render_template_string, url_for
from dataclasses import asdict
import time
import os
import DataVerificationAuction 

app = Flask(__name__)
# 实例化系统
system = DataVerificationAuction.VerificationSystem()

# HTML 模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Auction System</title>
</head>
<body>
    <h1>Auction System</h1>
    <!-- 添加区块表单 -->
    <form action="/add_block" method="post">
        Block ID: <input type="text" name="block_id"><br>
        Price: <input type="text" name="price"><br>
        Base Reward Rate: <input type="text" name="base_reward_rate"><br>
        Float Reward Rate: <input type="text" name="float_reward_rate"><br>
        Min Reward: <input type="text" name="min_reward"><br>
        Max Reward: <input type="text" name="max_reward"><br>
        ddl (seconds): <input type="text" name="ddl"><br>
        Growth Speed: <input type="text" name="growth_spd"><br>
        <input type="submit" value="Add Block">
    </form>
    <!-- 添加验证者表单 -->
    <form action="/add_verifier" method="post">
        Verifier ID: <input type="text" name="verifier_id"><br>
        Bid Price: <input type="text" name="bid_price"><br>
        <input type="submit" value="Add Verifier">
    </form>

    <h2>Blocks:</h2>
    <ul>
        {% for block in blocks %}
        <li>
            Block ID: {{ block.block_id }}<br>
            Price: {{ block.price }}<br>
            <!-- 其他区块属性... -->
            Verified: {{ 'Yes' if block.verified else 'No' }}
            <!-- 添加拍卖按钮 -->
            <form action="/start_auction/{{ block.block_id }}" method="post">
                <input type="submit" value="Start Auction for Block {{ block.block_id }}">
            </form>
        </li>
        {% endfor %}
    </ul>
    <h2>Blocks:</h2>
    <ul>
        {% for block in blocks %}
        <li>{{ block.block_id }} - {{ block.price }} - {{ block.ddl }} - {{ block.verified }}</li>
        {% endfor %}
    </ul>
    <h2>Verifiers:</h2>
    <ul>
        {% for verifier in verifiers %}
        <li>{{ verifier.verifier_id }} - {{ verifier.bid_price }} - {{ verifier.total_score }}</li>
        {% endfor %}
    </ul>
</body>
</html>
"""

@app.route('/')
def index():
    blocks = [asdict(block) for block in system.blocks]
    verifiers = [asdict(verifier) for verifier in system.verifiers]
    return render_template_string(HTML_TEMPLATE, blocks=blocks, verifiers=verifiers)

@app.route('/add_block', methods=['POST'])
def add_block():
    # 从表单获取数据并创建区块
    block_data = request.form.to_dict()
    block_data['block_id'] = int(block_data.get('block_id'))
    block_data['price'] = float(block_data.get('price'))
    block_data['base_reward_rate'] = float(block_data.get('base_reward_rate'))
    block_data['float_reward_rate'] = float(block_data['float_reward_rate'])
    block_data['min_reward'] = float(block_data['min_reward'])
    block_data['max_reward'] = float(block_data['max_reward'])
    block_data['ddl'] = int(block_data['ddl'])
    block_data['growth_spd'] = float(block_data['growth_spd'])
    
    block = DataVerificationAuction.DataBlock(**block_data)
    system.add_block(block)
    return index()

@app.route('/add_verifier', methods=['POST'])
def add_verifier():
    # 从表单获取数据并创建验证者
    verifier_data = request.form.to_dict()
    verifier_data['verifier_id'] = int(verifier_data.get('verifier_id'))
    verifier_data['bid_price'] = float(verifier_data['bid_price'])
    verifier = DataVerificationAuction.Verifier(**verifier_data)
    system.add_verifier(verifier)
    return index()

@app.route('/start_auction/<int:block_id>', methods=['GET'])
def start_auction(block_id):
    # 激活荷兰式拍卖系统
    system.scan_for_verification()
    
    
if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000), host='127.0.0.1')