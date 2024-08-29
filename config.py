import json
from web3 import Web3
import abis as abis


MIN_BLOCK_DIFF = 100
BLOCK_INCREMENT = 1000


       
with open("config.json", "r") as jsonFile:
    config = json.load(jsonFile) 

with open("blocks_synced.json", "r") as jsonFile:
    blocks_synced = json.load(jsonFile) 

def update_synced_block():
    with open("blocks_synced.json", "w") as jsonFile:
        json.dump(blocks_synced, jsonFile)