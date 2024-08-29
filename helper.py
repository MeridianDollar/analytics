from web3 import Web3
import json
import abis
import requests


CONVERSION_FACTOR =  10 ** 18

with open("config.json", "r") as jsonFile:
    config = json.load(jsonFile) 
    
def check_provider(rpc_list):
    """Iterate through the RPC list to find a working provider."""
    for rpc in rpc_list:
        try:
            provider = Web3(Web3.HTTPProvider(rpc))
            # Test the connection
            provider.eth.blockNumber
            return provider
        except requests.exceptions.RequestException as e:
            print(f"RPC Error: {e} - RPC: {rpc}")
        except Exception as e:
            print(f"Unexpected error: {e} - RPC: {rpc}")
            continue
    raise RuntimeError("All RPC endpoints failed.")




# Task 1: Open a trove
def fetchTroveStatus(address):
    troveManger = w3.eth.contract(address=config["troveManager"], abi=abis.troveManager())
    troveStatus = troveManger.functions.getTroveStatus(address).call() 
    if troveStatus == 1:
        return True
    else:
        return False 


# Task 2: Stake $150 or more  in stability pool
# Task 1: Open a trove
def fetchStabilityPool_150(address):
    stabilityPool = w3.eth.contract(address=config["stabilityPool"], abi=abis.stabilityPool())
    stake_in_wei = stabilityPool.functions.deposits(address).call() 
    stake_in_ether = stake_in_wei[0] / CONVERSION_FACTOR
    if stake_in_ether >= 150:
        return True
    else:
        return False 
    
    
# Task 3: Stake $500 or more  in stability pool
def fetchStabilityPool_500(address):
    stabilityPool = w3.eth.contract(address=config["stabilityPool"], abi=abis.stabilityPool())
    stake_in_wei = stabilityPool.functions.deposits(address).call() 
    stake_in_ether = stake_in_wei[0] / CONVERSION_FACTOR
    if stake_in_ether >= 500:
        return True
    else:
        return False 
    
    
# Task 4: Stake $1000 or more  in stability pool
def fetchStabilityPool_1000(address):
    stabilityPool = w3.eth.contract(address=config["stabilityPool"], abi=abis.stabilityPool())
    stake_in_wei = stabilityPool.functions.deposits(address).call() 
    stake_in_ether = stake_in_wei[0] / CONVERSION_FACTOR
    if stake_in_ether >= 1000:
        return True
    else:
        return False 
    
    
# Task 5 Stake 1000 MST to earn protocol rewards
def fetchStakingPool_1000(address):
    stakingPool = w3.eth.contract(address=config["stakingPool"], abi=abis.stakingPool())
    stake_in_wei = stakingPool.functions.getMstStake(address).call() 
    print(stake_in_wei)
    stake_in_ether = stake_in_wei / CONVERSION_FACTOR
    print(stake_in_ether)
    if stake_in_ether >= 1000:
        return True
    else:
        return False 
    
    
# Task 6 Stake 2500 MST to earn protocol rewards
def fetchStakingPool_2500(address):
    stakingPool = w3.eth.contract(address=config["stakingPool"], abi=abis.stakingPool())
    stake_in_wei = stakingPool.functions.getMstStake(address).call() 
    print(stake_in_wei)
    stake_in_ether = stake_in_wei / CONVERSION_FACTOR
    print(stake_in_ether)
    if stake_in_ether >= 2500:
        return True
    else:
        return False 
    
    
# Task 7 Stake 5000 MST to earn protocol rewards
def fetchStakingPool_5000(address):
    stakingPool = w3.eth.contract(address=config["stakingPool"], abi=abis.stakingPool())
    stake_in_wei = stakingPool.functions.getMstStake(address).call() 
    print(stake_in_wei)
    stake_in_ether = stake_in_wei / CONVERSION_FACTOR
    print(stake_in_ether)
    if stake_in_ether >= 5000:
        return True
    else:
        return False 



def write_to_json(new_data, file_path):
    try:
        with open(file_path, 'r') as file:
            # Attempt to load existing JSON data
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                # If the file is empty or invalid JSON, initialize with an empty list
                print(f"Warning: The file at {file_path} is empty or contains invalid JSON. Initializing with an empty list.")
                data = []
    except FileNotFoundError:
        # If the file does not exist, initialize with an empty list
        data = []

    # Create a dictionary for easier lookup and update of existing entries
    existing_combinations = {(entry['account'], entry['network']): entry for entry in data}

    # Flag to check if the file needs to be updated
    updated = False

    for new_entry in new_data:
        key = (new_entry['account'], new_entry['network'])
        # If healthFactor > 10000, skip updating/addition and remove existing high health factors
        if 'healthFactor' in new_entry and new_entry['healthFactor'] > 10000:
            if key in existing_combinations:
                del existing_combinations[key]
                updated = True
            continue

        if key in existing_combinations:
            # Update existing entry with new data
            existing_entry = existing_combinations[key]
            for field, value in new_entry.items():
                existing_entry[field] = value
            updated = True
        else:
            # Add new entries only if healthFactor <= 10000, which is already checked above
            existing_combinations[key] = new_entry
            updated = True

    # Reconstruct the data list from existing_combinations to reflect any removals
    updated_data = list(existing_combinations.values())

    # Sort the list by healthFactor from lowest to highest before writing
    sorted_data = sorted(updated_data, key=lambda x: x.get('healthFactor', float('inf')))

    # Write back to the file if there were any updates
    if updated:
        with open(file_path, 'w') as file:
            json.dump(sorted_data, file, indent=4)
            
            
