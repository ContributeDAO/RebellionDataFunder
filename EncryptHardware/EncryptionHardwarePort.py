
import serial
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import time
import hashlib
import os

class EncryptionHardwarePort:
    def __init__(self, port, baud_rate):
        self.ser = serial.Serial(port, baud_rate, timeout=1)


    def send_command(self,command_prefix: bytes, param: bytes):
        """
        发送命令到串口并等待响应。
        :param command_prefix: 命令前缀的字节序列。
        :param param: 参数数据字节序列。
        :return: 从串口接收到的响应。
        """
        self.ser.write(command_prefix + param)
        print(f"Sent command: {(command_prefix + param).hex()}")
        time.sleep(0.1)  # 等待设备响应，根据实际情况调整延时
        response = self.ser.read_all()  # 读取所有可用数据
        if response == b'\x00' * response.count(b'\x00'):
            print("Device exception: The response is all zeros.")
        else:
            # 打印接收到的数据的十六进制表示
            print("Received response:", response.hex())  
        return response


    def generate_key_pair(self,key_id: int):
        """
        生成密钥对 (NK)。
        """
        if(key_id>127):
            print("密钥对编号>127,最多支持128个编号！")
            return 0    
        command = bytes.fromhex('4E 4B') + key_id.to_bytes(1, 'big')
        return self.send_command(command, b'')


    def read_public_key(self,key_id: int):
        """
        读取公钥 (RP)。
        """
        if(key_id>127):
            print("密钥对编号>127,最多支持128个编号！")
            return 0    
        command = bytes.fromhex('52 50 ')  
        return self.send_command(command, key_id.to_bytes(1, 'big'))


    def decompress_public_key(self,compressed_key: bytes):
        """
        解压公钥 (DP)。
        """
        command = bytes.fromhex('44 50 ')
        return self.send_command(command, compressed_key)


    def sign_hash(self,key_id: int, hash_value: bytes):
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
        return self.send_command(command_prefix, key_id_bytes +  hash_value_bytes)

    def verify_signature(self,public_key: bytes, signature: bytes, hash_value: bytes):
        """
        验证签名 (VS)。
        """
        command_prefix = bytes.fromhex('56 53 ')
        # public_key_length = len(public_key).to_bytes(2, 'big', signed=True)
        # signature_length = len(signature).to_bytes(2, 'big', signed=True)
        # hash_length = len(hash_value).to_bytes(2, 'big', signed=True)
        return self.send_command(command_prefix, public_key +  signature +  hash_value)

    def output_random_number(self):
        """
        输出随机数 (OR)。
        """
        command_prefix = bytes.fromhex('4F 52')
        return self.send_command(command_prefix, b'')

    def set_random_number_mode(self,mode: int):
        """
        随机数模式 (BR)。0x59：伪随机数模式,其他：真随机数模式
        """
        mode_byte = mode.to_bytes(1, 'big', signed=True)
        command_prefix = bytes.fromhex('42 52')
        return self.send_command(command_prefix, mode_byte)

    def set_output_random_number_count(true_random_count: int, pseudo_random_count: int):
        """
        输出随机数数量 (ON)。
        """
        command_prefix = bytes.fromhex('4F 4E')
        true_random_count_bytes = true_random_count.to_bytes(4, 'big', signed=True)
        pseudo_random_count_bytes = pseudo_random_count.to_bytes(4, 'big', signed=True)
        return self.send_command(command_prefix , b'')

    def delete_key_pair(self,key_id: int):
        """
        删除密钥对 (DK)。
        """
        if(key_id>127):
            print("密钥对编号>127,最多支持128个编号！")
            return 0    
        key_id_bytes = key_id.to_bytes(1, 'big')
        command_prefix = bytes.fromhex('44 4B')
        return self.send_command(command_prefix, key_id_bytes)




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

# port = 'COM5'  # 串口号，Linux 下可能是 '/dev/ttyUSB0'
# baudrate = 460800
# ser = serial.Serial(port, baud_rate, timeout=1)