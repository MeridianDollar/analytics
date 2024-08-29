from config import *
from helper import *

def update_borrowers():
    
    networks = list(config.keys())

    for network in networks:
        if config[network]["analytics_required"]:
            try:
                w3 = check_provider(config[network]["rpcs"])
            except RuntimeError as e:
                print(f"Failed to connect to any RPC for network: {network}")
                continue
            
            last_synced_block = blocks_synced[network]
            lendingPool = w3.eth.contract(address=config[network]["contracts"]["lendingPool"], abi=abis.lendingPool())
            
            all_borrowers = set()
            while last_synced_block <= w3.eth.blockNumber:
                print(last_synced_block, "last_synced_block")  
                
                to_block = min(last_synced_block + BLOCK_INCREMENT, w3.eth.blockNumber)
                try:
                    events = lendingPool.events.Borrow().getLogs(fromBlock=last_synced_block, toBlock=to_block)
                    deposit_events = lendingPool.events.Deposit().getLogs(fromBlock=last_synced_block, toBlock=to_block)
                    withdraw_events = lendingPool.events.Withdraw().getLogs(fromBlock=last_synced_block, toBlock=to_block)

                except (requests.exceptions.RequestException, ValueError) as e:
                    print(f"Error fetching logs: {e}")
                    try:
                        w3 = check_provider(config[network]["rpcs"])
                        lendingPool = w3.eth.contract(address=config[network]["contracts"]["lendingPool"], abi=abis.lendingPool())
                        continue
                    except RuntimeError:
                        print(f"All RPC connections failed for network {network}")
                        break

                unique_users = {event['args']['onBehalfOf'] for event in events}
                all_borrowers.update(unique_users)
                
                if to_block == w3.eth.blockNumber or w3.eth.blockNumber - to_block < MIN_BLOCK_DIFF:
                    blocks_synced[network] = to_block
                    update_synced_block()
                    break
                else:
                    last_synced_block = to_block + 1

            # Retrieve user positions and store in a list
            user_positions = [
                {
                    "account": borrower,
                    "healthFactor": lendingPool.functions.getUserAccountData(borrower).call()[5] / CONVERSION_FACTOR,
                    "network": network
                }
                for borrower in all_borrowers
            ]
            
            # print(user_positions)

            write_to_json(user_positions, "borrowers.json")

update_borrowers()

# Initial block when contract was deployed: 253681
