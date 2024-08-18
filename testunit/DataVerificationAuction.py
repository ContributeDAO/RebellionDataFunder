from dataclasses import dataclass, field
from queue import Full
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

    def scan_for_verification(self)-> List[DataBlock]:
        up_for_auction: List[DataBlock]=[]
        # 检索所有未验证且在DDL内的区块，将它们加入待验证列表
        current_time = int(time.time())
        for block in self.blocks:
            if not block.verified and current_time <= block.ddl:
                up_for_auction.append(block)
        return up_for_auction
        
    def calculate_reward(self, block: DataBlock, current_time: int) -> float:
        t = current_time- block.creation_time
        T = block.ddl - block.creation_time
        reward = (block.min_reward + (block.max_reward - block.min_reward) * (sigmoid((t / T),block.growth_spd)))
        return block.price * (block.base_reward_rate + block.float_reward_rate) * reward

    def verify_block(self, block: DataBlock, verifier: Verifier):
        # 只在待验证列表中操作
        current_time = int(time.time())
        reward = self.calculate_reward(block, current_time)
        if verifier.bid_price <= reward:
            verifier.total_score += reward
            block.verified = True  # 修改状态为已验证
            #test 验证成功则提高报价
            verifier.bid_price = reward+1
            print(f"Verifier {verifier.verifier_id} verified block {block.block_id} and earned {reward:.2f} points.")
            return True
        print(f"verifier ={verifier.verifier_id} verifier.bid_price={verifier.bid_price} verification failed for block_id ={block.block_id},now reward={reward:.2f}.")
        return False

    def start_auction(self):
        # 拍卖逻辑
        print("start auction")
        start_time = time.time()
        while time.time() - start_time < 60:  # 假设拍卖持续1分钟
            self.up_for_auction=self.scan_for_verification()
            if(self.up_for_auction.__len__==0):
                return
            for block in self.up_for_auction:
                for verifier in self.verifiers:
                    if(self.verify_block(block, verifier)):
                        break
            # 这里可以添加逻辑来接受出价和选择胜出的验证者
            time.sleep(1)  # 每秒检查一次
            
        for verifier in self.verifiers:
            print(verifier)


# 示例
system = VerificationSystem()

# 添加区块和验证者
block1 = DataBlock(block_id=1, price=10.0, base_reward_rate=0.05, float_reward_rate=0.02,
                   min_reward=1.0, max_reward=10.0, ddl=int(time.time()+60))
block2 = DataBlock(block_id=2, price=10.0, base_reward_rate=0.05, float_reward_rate=0.03,
                   min_reward=1.0, max_reward=10.0, ddl=int(time.time()+60))
block3 = DataBlock(block_id=2, price=10.0, base_reward_rate=0.05, float_reward_rate=0.03,
                   min_reward=1.0, max_reward=10.0, ddl=int(time.time()+60))



system.add_block(block1)
system.add_block(block2)
system.add_block(block3)

verifier1 = Verifier(verifier_id=1, bid_price=4.0)
verifier2 = Verifier(verifier_id=2, bid_price=5.0)
system.add_verifier(verifier1)
system.add_verifier(verifier2)

system.start_auction()
