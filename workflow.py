### Define workflow ###
from typing import Dict, List

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

### Preload workflows ###
import os
import json

workflows = []
workflow_folder = "workflows/"

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

### Initialize workflow ###
import sys
from datetime import datetime
import requests
import time
import random

curr_workflow_id = sys.argv[1]

# Robots addresses            
KIP_ADDRESS = '192.168.4.50:5000'
GIMI_ADDRESS = '192.168.4.99:5000'
ARM_ADDRESS = '192.168.4.114:5000'

USER = 'user'
GIMI = 'gimi'
KIP = 'kip'

# ARM position change to +90, -90, +135, -135
GIMI_TO_USER = -135
GIMI_TO_KIP = 90
KIP_TO_USER = 135
KIP_TO_GIMI = -90
USER_TO_GIMI = 135
USER_TO_KIP = -135

# ARM initial position
ARM_INIT_POSITION = 1900

# Create a folder for logs
logs_folder = "logs/"
os.makedirs(logs_folder, exist_ok=True)
logs = []


ball_from = USER
ball_to= ball_from

# Find the selected workflow based on the provided ID
workflow = next((workflow for workflow in workflows if workflow.id == curr_workflow_id), None)

# Create a timestamp for the log file name
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
log_file_name = f"logs_{curr_workflow_id}_{timestamp}.txt"

#def initialize(animation_kip, animation_gimi, position_arm):
#    requests.post(f'http://{KIP_ADDRESS}/api/robot/animations/{animation_kip}')
#    requests.post(f'http://{GIMI_ADDRESS}/api/robot/animations/{animation_gimi}')
#    requests.post(f'http://{ARM_ADDRESS}/api/robot/init/{position_arm}')

import concurrent.futures

def initialize(animation_kip, animation_gimi, position_arm):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(requests.post, f'http://{KIP_ADDRESS}/api/robot/animations/{animation_kip}'),
            executor.submit(requests.post, f'http://{GIMI_ADDRESS}/api/robot/animations/{animation_gimi}'),
            executor.submit(requests.post, f'http://{ARM_ADDRESS}/api/robot/init/{position_arm}')
        ]
        concurrent.futures.wait(futures)
    

#def makeRequest(ball_from, ball_to, animation_kip, animation_gimi, angle_arm):
#    requests.post(f'http://{KIP_ADDRESS}/api/robot/animations/{animation_kip}')
#    requests.post(f'http://{GIMI_ADDRESS}/api/robot/animations/{animation_gimi}')
#    #requests.post(f'http://{ARM_ADDRESS}/api/robot/move/{angle_arm}')
#    log_entry = f"{datetime.now()} - {ball_from} to {ball_to}: {KIP_ADDRESS}/robot/animations/{animation_kip}, {GIMI_ADDRESS}/robot/animations/{animation_gimi}, {ARM_ADDRESS}/robot/move/{angle_arm}"
#    logs.append(log_entry)
#    #print(ball_to + " - " + ball_from)

def makeRequest(ball_from, ball_to, animation_kip, animation_gimi, angle_arm):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submeter as chamadas HTTP para execução simultânea
        futures = [
            executor.submit(requests.post, f'http://{KIP_ADDRESS}/api/robot/animations/{animation_kip}'),
            executor.submit(requests.post, f'http://{GIMI_ADDRESS}/api/robot/animations/{animation_gimi}'),
            executor.submit(requests.post, f'http://{ARM_ADDRESS}/api/robot/move/{angle_arm}')
        ]
        
        concurrent.futures.wait(futures)
        time.sleep(2)
        log_entry = f"{datetime.now()} - {ball_from} to {ball_to}: {KIP_ADDRESS}/robot/animations/{animation_kip}, {GIMI_ADDRESS}/robot/animations/{animation_gimi}, {ARM_ADDRESS}/robot/move/{angle_arm}"
        logs.append(log_entry)


# Initialize robots
initialize("pre_start_kip","pre_start_gimi", ARM_INIT_POSITION)
time.sleep(2)
initialize("start_kip","start_gimi", ARM_INIT_POSITION)

# Define getch function
if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

for config in workflow.configs:
    for i in range(config.num_interations):
        if ball_from == USER:
            print("Choose 0 (KIP) or 1 (GIMI): ")
            inp = getch()
            if inp == "0":
                print("You chose KIP")
                ball_to = KIP
            elif inp == "1":
                print("You chose GIMI")
                ball_to = GIMI
                
        else:
            options = config.options[ball_from]
            chosen_option = random.choices(options, weights=[option["weight"] for option in options], k=1)[0]
            ball_to = chosen_option["to"]
            
        if ball_from == USER and ball_to == KIP:
            makeRequest(ball_from,ball_to,"user_to_kip_kip","user_to_kip_gimi",USER_TO_KIP)
        elif ball_from == USER and ball_to == GIMI:
            makeRequest(ball_from,ball_to,"user_to_gimi_kip","user_to_gimi_gimi",USER_TO_GIMI)
        elif ball_from == KIP and ball_to == USER:
            makeRequest(ball_from,ball_to,"kip_to_user_kip","kip_to_user_gimi",KIP_TO_USER)
        elif ball_from == KIP and ball_to == GIMI:
            makeRequest(ball_from,ball_to,"kip_to_gimi_kip","kip_to_gimi_gimi",KIP_TO_GIMI)
        elif ball_from == GIMI and ball_to == USER:
            makeRequest(ball_from,ball_to,"gimi_to_user_kip","gimi_to_user_gimi",GIMI_TO_USER)
        elif ball_from == GIMI and ball_to == KIP:
            makeRequest(ball_from,ball_to,"gimi_to_kip_kip","gimi_to_kip_gimi",GIMI_TO_KIP)
            
        ball_from = ball_to
    
# Save the logs to a file in the logs folder with timestamped name
log_file_path = os.path.join(logs_folder, log_file_name)
with open(log_file_path, "w") as log_file:
    log_file.write("\n".join(logs))