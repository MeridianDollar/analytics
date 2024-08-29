from config import *
from helper import *

def update_borrowers():
    networks = list(config.keys())

    # To store total volume for each token across all networks
    total_borrow_volumes = {}
    total_deposit_volumes = {}
    total_withdraw_volumes = {}
    total_repay_volumes = {}

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
                    # Fetch events for Borrow, Deposit, Withdraw, and Repay
                    events = lendingPool.events.Borrow().getLogs(fromBlock=last_synced_block, toBlock=to_block)
                    deposit_events = lendingPool.events.Deposit().getLogs(fromBlock=last_synced_block, toBlock=to_block)
                    withdraw_events = lendingPool.events.Withdraw().getLogs(fromBlock=last_synced_block, toBlock=to_block)
                    repay_events = lendingPool.events.Repay().getLogs(fromBlock=last_synced_block, toBlock=to_block)

                except (requests.exceptions.RequestException, ValueError) as e:
                    print(f"Error fetching logs: {e}")
                    try:
                        w3 = check_provider(config[network]["rpcs"])
                        lendingPool = w3.eth.contract(address=config[network]["contracts"]["lendingPool"], abi=abis.lendingPool())
                        continue
                    except RuntimeError:
                        print(f"All RPC connections failed for network {network}")
                        break

                # Process Borrow events
                for event in events:
                    reserve = event['args']['reserve']
                    amount = event['args']['amount']

                    # Get the token configuration for the reserve address
                    token_info = None
                    for token, data in config[network].get("lending_tokens", {}).items():
                        if data["token"].lower() == reserve.lower():
                            token_info = data
                            break

                    # If token found in the config, adjust amount by decimals
                    if token_info:
                        decimals = token_info['decimals']
                        adjusted_amount = amount / (10 ** decimals)

                        # Add the adjusted amount to the total borrow volume for the token
                        if reserve not in total_borrow_volumes:
                            total_borrow_volumes[reserve] = 0
                        total_borrow_volumes[reserve] += adjusted_amount

                # Process Deposit events
                for event in deposit_events:
                    reserve = event['args']['reserve']
                    amount = event['args']['amount']

                    # Get the token configuration for the reserve address
                    token_info = None
                    for token, data in config[network].get("lending_tokens", {}).items():
                        if data["token"].lower() == reserve.lower():
                            token_info = data
                            break

                    # If token found in the config, adjust amount by decimals
                    if token_info:
                        decimals = token_info['decimals']
                        adjusted_amount = amount / (10 ** decimals)

                        # Add the adjusted amount to the total deposit volume for the token
                        if reserve not in total_deposit_volumes:
                            total_deposit_volumes[reserve] = 0
                        total_deposit_volumes[reserve] += adjusted_amount

                # Process Withdraw events
                for event in withdraw_events:
                    reserve = event['args']['reserve']
                    amount = event['args']['amount']

                    # Get the token configuration for the reserve address
                    token_info = None
                    for token, data in config[network].get("lending_tokens", {}).items():
                        if data["token"].lower() == reserve.lower():
                            token_info = data
                            break

                    # If token found in the config, adjust amount by decimals
                    if token_info:
                        decimals = token_info['decimals']
                        adjusted_amount = amount / (10 ** decimals)

                        # Add the adjusted amount to the total withdraw volume for the token
                        if reserve not in total_withdraw_volumes:
                            total_withdraw_volumes[reserve] = 0
                        total_withdraw_volumes[reserve] += adjusted_amount

                # Process Repay events
                for event in repay_events:
                    reserve = event['args']['reserve']
                    amount = event['args']['amount']

                    # Get the token configuration for the reserve address
                    token_info = None
                    for token, data in config[network].get("lending_tokens", {}).items():
                        if data["token"].lower() == reserve.lower():
                            token_info = data
                            break

                    # If token found in the config, adjust amount by decimals
                    if token_info:
                        decimals = token_info['decimals']
                        adjusted_amount = amount / (10 ** decimals)

                        # Add the adjusted amount to the total repay volume for the token
                        if reserve not in total_repay_volumes:
                            total_repay_volumes[reserve] = 0
                        total_repay_volumes[reserve] += adjusted_amount

                # Update list of unique users
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
            
            write_to_json(user_positions, "borrowers.json")

    # Print the total borrow volumes for each token
    for token, volume in total_borrow_volumes.items():
        print(f"Total borrow volume for token {token}: {volume}")

    # Print the total deposit volumes for each token
    for token, volume in total_deposit_volumes.items():
        print(f"Total deposit volume for token {token}: {volume}")

    # Print the total withdraw volumes for each token
    for token, volume in total_withdraw_volumes.items():
        print(f"Total withdraw volume for token {token}: {volume}")

    # Print the total repay volumes for each token
    for token, volume in total_repay_volumes.items():
        print(f"Total repay volume for token {token}: {volume}")

update_borrowers()
