import serial


from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

import hashlib
import os

import time
port = 'COM5'  # 串口号，Linux 下可能是 '/dev/ttyUSB0'
baudrate = 460800

# 打开串口
ser = serial.Serial(port, baudrate, timeout=1)

def send_command(command_prefix: bytes, param: bytes):
    """
    发送命令到串口并等待响应。
    :param command_prefix: 命令前缀的字节序列。
    :param param: 参数数据字节序列。
    :return: 从串口接收到的响应。
    """
    ser.write(command_prefix + param)
    print(f"Sent command: {(command_prefix + param).hex()}")
    time.sleep(0.1)  # 等待设备响应，根据实际情况调整延时
    response = ser.read_all()  # 读取所有可用数据
    if response == b'\x00' * response.count(b'\x00'):
        print("Device exception: The response is all zeros.")
    else:
        # 打印接收到的数据的十六进制表示
        print("Received response:", response.hex())  
    return response


def generate_key_pair(key_id: int):
    """
    生成密钥对 (NK)。
    """
    if(key_id>127):
        print("密钥对编号>127,最多支持128个编号！")
        return 0    
    command = bytes.fromhex('4E 4B') + key_id.to_bytes(1, 'big')
    return send_command(command, b'')


def read_public_key(key_id: int):
    """
    读取公钥 (RP)。
    """
    if(key_id>127):
        print("密钥对编号>127,最多支持128个编号！")
        return 0    
    command = bytes.fromhex('52 50 ')  
    return send_command(command, key_id.to_bytes(1, 'big'))


def decompress_public_key(compressed_key: bytes):
    """
    解压公钥 (DP)。
    """
    command = bytes.fromhex('44 50 ')
    return send_command(command, compressed_key)


def sign_hash(key_id: int, hash_value: bytes):
    """
    签名 (SH)。
    """
    if(key_id > 127):
        print("密钥对编号>127,最多支持128个编号！")
        return 0    
    key_id_bytes = key_id.to_bytes(1, 'big')
    command_prefix = bytes.fromhex('53 48 ')
    hash_value_bytes = hash_value.encode('utf-8')  # 确保hash_value是bytes类型
    #hash_length = len(hash_value).to_bytes(1, 'big', signed=True)
    return send_command(command_prefix, key_id_bytes +  hash_value_bytes)

def verify_signature(public_key: bytes, signature: bytes, hash_value: bytes):
    """
    验证签名 (VS)。
    """
    command_prefix = bytes.fromhex('56 53 ')
    # public_key_length = len(public_key).to_bytes(2, 'big', signed=True)
    # signature_length = len(signature).to_bytes(2, 'big', signed=True)
    # hash_length = len(hash_value).to_bytes(2, 'big', signed=True)
    return send_command(command_prefix, public_key +  signature +  hash_value)

def output_random_number():
    """
    输出随机数 (OR)。
    """
    command_prefix = bytes.fromhex('4F 52')
    return send_command(command_prefix, b'')

def set_random_number_mode(mode: int):
    """
    随机数模式 (BR)。0x59：伪随机数模式,其他：真随机数模式
    """
    mode_byte = mode.to_bytes(1, 'big', signed=True)
    command_prefix = bytes.fromhex('42 52')
    return send_command(command_prefix, mode_byte)

def set_output_random_number_count(true_random_count: int, pseudo_random_count: int):
    """
    输出随机数数量 (ON)。
    """
    command_prefix = bytes.fromhex('4F 4E')
    true_random_count_bytes = true_random_count.to_bytes(4, 'big', signed=True)
    pseudo_random_count_bytes = pseudo_random_count.to_bytes(4, 'big', signed=True)
    return send_command(command_prefix , b'')

def delete_key_pair(key_id: int):
    """
    删除密钥对 (DK)。
    """
    if(key_id>127):
        print("密钥对编号>127,最多支持128个编号！")
        return 0    
    key_id_bytes = key_id.to_bytes(1, 'big')
    command_prefix = bytes.fromhex('44 4B')
    return send_command(command_prefix, key_id_bytes)




def get_file_hash(file_path: str, hash_algorithm: str = 'sha256') -> str:
    """
    提取文件的哈希摘要。
    
    :param file_path: 文件路径，相对于当前工作目录。
    :param hash_algorithm: 哈希算法，默认为 'sha256'。
    :return: 文件的哈希摘要。
    """
    # 支持的哈希算法
    hash_algorithms = {
        'md5': hashlib.md5,
        'sha1': hashlib.sha1,
        'sha256': hashlib.sha256,
        'sha512': hashlib.sha512
    }
    
    # 获取哈希对象
    hash_func = hash_algorithms.get(hash_algorithm.lower())
    if not hash_func:
        raise ValueError(f"Unsupported hash algorithm: {hash_algorithm}")

    # 检查文件是否存在
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"No such file: '{file_path}'")

    # 打开文件并读取内容
    with open(file_path, 'rb') as file:
        buffer = file.read(4096)
        hash_obj = hash_func()
        while buffer:
            hash_obj.update(buffer)
            buffer = file.read(4096)
    
    # 获取哈希摘要
    return hash_obj.hexdigest()










if ser.isOpen():
    print(f"Opened {port} at {baudrate} baud")

    try:
        # # 要发送的数据，十六进制转换为字节
        # send_data = bytes.fromhex('52 50 00')
        
        # # 发送数据
        # ser.write(send_data)
        # print("Data sent:", send_data.hex())

        # # 等待设备响应，可以根据实际情况调整延时
        # time.sleep(0.5)  # 例如，等待500毫秒

        # # 读取数据，这里使用readline来读取一行数据
        # response = ser.readline()
        
        # # 检查响应是否全0

        # response = generate_key_pair(0)
        # response = generate_key_pair(1)
        # response = generate_key_pair(2)
        # response = generate_key_pair(3)
        # response = generate_key_pair(4)
        response = read_public_key(4)
        # response = decompress_public_key(response)

        # response =  set_random_number_mode(0x59)
        # response = output_random_number()
        # response = set_output_random_number_count(4,4)
        # response =  set_random_number_mode(0x01)
        # response = output_random_number()       
        # response = delete_key_pair(2)

# 示例：提取文件的SHA-256哈希值
        file_path = './testunit/example.txt'  # 相对于当前工作目录的文件路径
        try:
            hash_value = get_file_hash(file_path, 'sha256')
            print(f"The SHA-256 hash of the file is: {hash_value}")
        except FileNotFoundError as e:
            print(f"File not found: {e}")
        except ValueError as e:
            print(f"Value error: {e}")


        signature = sign_hash(4, hash_value)
        print(f"File hash: {hash_value}")
        print(f"Signature: {signature.hex()}")



        # if response == b'\x00' * response.count(b'\x00'):
        #     print("Device
        #     # 打印接收到的数据的十六进制表示
        #     print("Received response:", response.hex())

    except KeyboardInterrupt:
        print("Exiting...")

    finally:
        # 关闭串口
        ser.close()
        print("Closed port")
else:
    print("Failed to open port")