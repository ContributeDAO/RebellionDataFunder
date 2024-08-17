from dataclasses import dataclass, field
import time
from typing import List

import math

# 定义S型增长曲线函数
def sigmoid(x, k=1):
    return 1 / (1 + math.exp(-k * (2 * x - 1)))

@dataclass
class DataBlock:
    block_id: int
    price: float
    base_reward_rate: float
    float_reward_rate: float
    min_reward: float
    max_reward: float
    creation_time: int  # 区块创建时间（时间戳）
    ddl: int            # 最晚验证时间（时间戳）
    growth_spd: float = 1.0 # 奖励增长速度k
    verified: bool = False  # 是否已验证
    def __init__(self,block_id: int,price: float,base_reward_rate: float,float_reward_rate: float,min_reward: float,max_reward: float, ddl: int,growth_spd: float = 1.0):
         self.block_id = block_id
         self.price = price
         self.base_reward_rate = base_reward_rate
         self.float_reward_rate = float_reward_rate
         self.min_reward = min_reward
         self.max_reward = max_reward
         self.ddl = ddl
         self.growth_spd =growth_spd
         self.creation_time=time.time()
         
    def is_verifiable(self, current_time: int) -> bool:
        # 检查当前时间是否在创建时间和DDL之间
        return self.creation_time <= current_time <= self.ddl

    def calculate_reward(self, current_time: int) -> float:
        t = current_time - self.creation_time
        T = self.ddl - self.creation_time
        reward = (self.min_reward + (self.max_reward - self.min_reward) * ((t / T) ** self.growth_exponent))
        return self.price * (self.base_reward_rate + self.float_reward_rate) * reward

@dataclass
class Verifier:
    verifier_id: int
    total_score: float = 0.0
    bid_price: float = 0.0

    def make_bid(self, block: DataBlock, system: "VerificationSystem"):
        # 验证者对区块进行竞价
        if block.verified or not block.is_verifiable(time.time()):
            print("Bid rejected: Block is already verified or not within the verification window.")
            return False
        reward = block.calculate_reward(time.time())
        if self.bid_price <= reward:
            system.verify_block(block, self)
            total_score+=reward
            return True
        else:
            print(f"Bid rejected: Bid price {self.bid_price} is higher than the block reward {reward}.")
            return False

class VerificationSystem:
    def __init__(self):
        self.blocks: List[DataBlock] = []
        self.verifiers: List[Verifier] = []
        self.up_for_auction: List[DataBlock] = []  # 待验证区块列表

    def add_block(self, block: DataBlock):
        self.blocks.append(block)

    def add_verifier(self, verifier: Verifier):
        self.verifiers.append(verifier)

    def scan_for_verification(self):
        # 检索所有未验证且在DDL内的区块，将它们加入待验证列表
        current_time = int(time.time())
        self.up_for_auction = [block for block in self.blocks if not block.verified and current_time <= block.ddl]

    def calculate_reward(self, block: DataBlock, current_time: int) -> float:
        t = current_time- block.creation_time
        T = block.ddl - block.creation_time
        reward = (block.min_reward + (block.max_reward - block.min_reward) * (sigmoid((t / T),block.growth_spd)))
        return block.price * (block.base_reward_rate + block.float_reward_rate) * reward

    def verify_block(self, block_id: int, verifier_id: int):
        # 只在待验证列表中操作
        for block in self.up_for_auction:
            if block.block_id == block_id:
                current_time = int(time.time())
                reward = self.calculate_reward(block, current_time)
                verifier = next((v for v in self.verifiers if v.verifier_id == verifier_id), None)
                if verifier and verifier.bid_price >= reward:
                    verifier.total_score += reward
                    block.verified = True  # 修改状态为已验证
                    print(f"Verifier {verifier.verifier_id} verified block {block.block_id} and earned {reward:.2f} points.")
                    return True
        print(f"Verification failed for block_id {block_id}.")
        return False

    # 其他方法...

# 示例用法
system = VerificationSystem()

# # 添加区块和验证者
# block1 = DataBlock(block_id=1, price=10.0, base_reward_rate=0.05, float_reward_rate=0.02,
#                    min_reward=1.0, max_reward=10.0, ddl=int(120))
# system.add_block(block1)
# verifier1 = Verifier(verifier_id=1, bid_price=8.0)
# system.add_verifier(verifier1)

# # 扫描待验证区块
# system.scan_for_verification()

# # 尝试验证区块
# time.sleep(10)  # 等待10秒
# system.verify_block(block_id=1, verifier_id=1)

# # 检查区块是否需要重新加入验证池
# time.sleep(60)  # 等待超过DDL时间
# for block in system.blocks:
#     if time.time() > block.ddl and not block.verified:
#         print(f"Block {block.block_id} has not been verified and is no longer eligible for verification.")