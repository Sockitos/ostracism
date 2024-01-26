import random
from typing import Dict, List
from datetime import datetime
import sys
import requests

class MoveOption: 
    def __init__(
        self,
        to: str,
        weight: int,
    ):
        self.to = to
        self.weight = weight

class Config:
    def __init__(
        self,
        num_interations: int,
        options: Dict[str, List[MoveOption]],
    ):
        self.num_interations = num_interations
        self.options = options
        
class Workflow:
    def __init__(
        self,
        id: str,
        configs: List[Config],
    ): 
        self.id = id
        self.configs = configs

### Initialize workflow #############################################################################
workflows = []
workflow_folder = "workflows/"
curr_workflow_id = sys.argv[1]

import os
import json

for filename in os.listdir(workflow_folder):
    if filename.endswith(".json"):
        file_path = os.path.join(workflow_folder, filename)
        with open(file_path, "r") as file:
            
            workflow_data = json.load(file)
            workflow = Workflow(
                id=workflow_data.get('id'),
                configs=[Config(
                    num_interations=config.get('num_interations'),
                    options=config.get('options')
                ) for config in workflow_data.get('configs')]
            )
            workflows.append(workflow)
            
KIP_ADDRESS = 'kip.local'
GIMI_ADDRESS = 'gimi.local'
ARM_ADDRESS = 'arm.local'

USER = 'user'
GIMI = 'gimi'
KIP = 'kip'

TO_USER = 6130
TO_GIMI = 3430
TO_KIP = 4642 

ball_from = USER
ball_to= ball_from

# Create a folder for logs
logs_folder = "logs/"
os.makedirs(logs_folder, exist_ok=True)
logs = []

#Find the selected workflow based on the provided ID
workflow = next((workflow for workflow in workflows if workflow.id == curr_workflow_id), None)

# Create a timestamp for the log file name
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
log_file_name = f"logs_{curr_workflow_id}_{timestamp}.txt"

for config in workflow.configs:
    for i in range(config.num_interations):
        if ball_from == USER:
            inp = input("Choose 0 (KIP) or 1 (GIMI): ")
            if inp == "0":
                print("You chose KIP")
                ball_to = KIP
            elif inp == "1":
                print("You chose GIMI")
                ball_to = GIMI
                
        else:
            #print(config.options)
            options = config.options[ball_from]
            chosen_option = random.choices(options, weights=[option["weight"] for option in options], k=1)[0]
            ball_to = chosen_option["to"]
            
        if ball_from == USER and ball_to == KIP:
            requests.post(f'http://{KIP_ADDRESS}/robot/animations/user_to_kip_kip')
            requests.post(f'http://{GIMI_ADDRESS}/robot/animations/user_to_kip_gimi')
            requests.post(f'http://{ARM_ADDRESS}/robot/move/{TO_KIP}')
            log_entry = f"{datetime.now()} - {USER} to {KIP}: {KIP_ADDRESS}/robot/animations/user_to_kip_kip, {GIMI_ADDRESS}/robot/animations/user_to_kip_gimi, {ARM_ADDRESS}/robot/move/{TO_KIP}"
        elif ball_from == USER and ball_to == GIMI:
            requests.post(f'http://{KIP_ADDRESS}/robot/animations/user_to_gimi_kip')
            requests.post(f'http://{GIMI_ADDRESS}/robot/animations/user_to_gimi_gimi')
            requests.post(f'http://{ARM_ADDRESS}/robot/move/{TO_GIMI}')
            log_entry = f"{datetime.now()} - {USER} to {GIMI}: {KIP_ADDRESS}/robot/animations/user_to_gimi_kip, {GIMI_ADDRESS}/robot/animations/user_to_gimi_gimi, {ARM_ADDRESS}/robot/move/{TO_GIMI}"
        elif ball_from == KIP and ball_to == USER:
            requests.post(f'http://{KIP_ADDRESS}/robot/animations/kip_to_user_kip')
            requests.post(f'http://{GIMI_ADDRESS}/robot/animations/kip_to_user_gimi')
            requests.post(f'http://{ARM_ADDRESS}/robot/move/{TO_USER}')
            log_entry = f"{datetime.now()} - {KIP} to {USER}: {KIP_ADDRESS}/robot/animations/kip_to_user_kip, {GIMI_ADDRESS}/robot/animations/kip_to_user_gimi, {ARM_ADDRESS}/robot/move/{TO_USER}"
        elif ball_from == KIP and ball_to == GIMI:
            requests.post(f'http://{KIP_ADDRESS}/robot/animations/kip_to_gimi_kip')
            requests.post(f'http://{GIMI_ADDRESS}/robot/animations/kip_to_gimi_gimi')
            requests.post(f'http://{ARM_ADDRESS}/robot/move/{TO_GIMI}')
            log_entry = f"{datetime.now()} - {KIP} to {GIMI}: {KIP_ADDRESS}/robot/animations/kip_to_gimi_kip, {GIMI_ADDRESS}/robot/animations/kip_to_gimi_gimi, {ARM_ADDRESS}/robot/move/{TO_GIMI}"
        elif ball_from == GIMI and ball_to == USER:
            requests.post(f'http://{KIP_ADDRESS}/robot/animations/gimi_to_user_kip')
            requests.post(f'http://{GIMI_ADDRESS}/robot/animations/gimi_to_user_gimi')
            requests.post(f'http://{ARM_ADDRESS}/robot/move/{TO_USER}')
            log_entry = f"{datetime.now()} - {GIMI} to {USER}: {KIP_ADDRESS}/robot/animations/gimi_to_user_kip, {GIMI_ADDRESS}/robot/animations/gimi_to_user_gimi, {ARM_ADDRESS}/robot/move/{TO_USER}"
        elif ball_from == GIMI and ball_to == KIP:
            requests.post(f'http://{KIP_ADDRESS}/robot/animations/gimi_to_kip_kip')
            requests.post(f'http://{GIMI_ADDRESS}/robot/animations/gimi_to_kip_gimi')
            requests.post(f'http://{ARM_ADDRESS}/robot/move/{TO_KIP}')
            log_entry = f"{datetime.now()} - {GIMI} to {KIP}: {KIP_ADDRESS}/robot/animations/gimi_to_kip_kip, {GIMI_ADDRESS}/robot/animations/gimi_to_kip_gimi, {ARM_ADDRESS}/robot/move/{TO_KIP}"
            
        logs.append(log_entry)
            
        ball_from = ball_to
    
# Save the logs to a file in the logs folder with timestamped name
log_file_path = os.path.join(logs_folder, log_file_name)
with open(log_file_path, "w") as log_file:
    log_file.write("\n".join(logs))