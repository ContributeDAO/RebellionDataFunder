import hashlib
import sqlite3

# 数据库初始化
def init_db():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS data_info (
                 id TEXT PRIMARY KEY,
                 device_number TEXT,
                 fingerprint TEXT,
                 wallet_address TEXT)''')
    conn.commit()
    conn.close()

# 上传数据并存储
def upload_data(device_number, fingerprint, wallet_address):
    # 计算ID（hash）
    data_string = f"{device_number}{fingerprint}"
    data_id = hashlib.sha256(data_string.encode()).hexdigest()
    
    # 存储数据到本地数据库
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO data_info (id, device_number, fingerprint, wallet_address)
                 VALUES (?, ?, ?, ?)''',
              (data_id, device_number, fingerprint, wallet_address))
    conn.commit()
    conn.close()
    return data_id

# 从钱包地址查找数据标识
def find_data_id_by_wallet(wallet_address):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('''SELECT id FROM data_info WHERE wallet_address = ?''', (wallet_address,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

# 初始化数据库
init_db()

# 示例用法
device_number = '123456'
fingerprint = 'abcdef'
wallet_address = 'wallet_address_example'

# 上传数据
data_id = upload_data(device_number, fingerprint, wallet_address)
print(f"Data ID: {data_id}")

# 通过钱包地址查找数据标识
found_id = find_data_id_by_wallet(wallet_address)
print(f"Found Data ID: {found_id}")
