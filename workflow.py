import random
from typing import Dict, List

import requests

USER = 'user'
GIMI = 'gimi'
KIP = 'kip'

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
    

workflow = Workflow(
    id = 'test',
    configs = [
        Config(
            num_interations = 5,
            options = {
                GIMI: [
                    MoveOption(to = USER, weight = 1),
                    MoveOption(to = KIP, weight = 10),
                ],
                KIP: [
                    MoveOption(to = USER, weight = 1),
                    MoveOption(to = GIMI, weight = 10),
                ],
            },
        ),
        Config(
            num_interations = 5,
            options = {
                GIMI: [
                    MoveOption(to = USER, weight = 10),
                    MoveOption(to = KIP, weight = 1),
                ],
                KIP: [
                    MoveOption(to = USER, weight = 10),
                    MoveOption(to = GIMI, weight = 1),
                ],
            },
        ),
    ],
)


KIP_ADDRESS = 'kip.local'
GIMI_ADDRESS = 'gimi.local'
ARM_ADDRESS = 'arm.local'

KIP_ANIMATION1 = 'kip_animation1'
KIP_ANIMATION2 = 'kip_animation1'

GIMI_ANIMATION1 = 'gimi_animation1'
GIMI_ANIMATION2 = 'gimi_animation1'

ARM_ANGLE1 = 0
ARM_ANGLE2 = 180

ball_from = USER
ball_to= ball_from

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
            options = config.options[ball_from]
            ball_to = random.choices([option.to for option in options], weights = [option.weight for option in options])
            
        if ball_from == USER and ball_to == KIP:
            requests.post(f'http://{KIP_ADDRESS}/robot/animations/{KIP_ANIMATION1}')
            requests.post(f'http://{GIMI_ADDRESS}/robot/animations/{KIP_ANIMATION1}')
            requests.post(f'http://{ARM_ADDRESS}/robot/move/{ARM_ANGLE1}')
        elif ball_from == USER and ball_to == GIMI:
            requests.post(f'http://{KIP_ADDRESS}/robot/animations/{KIP_ANIMATION1}')
            requests.post(f'http://{GIMI_ADDRESS}/robot/animations/{KIP_ANIMATION1}')
            requests.post(f'http://{ARM_ADDRESS}/robot/move/{ARM_ANGLE1}')
        elif ball_from == KIP and ball_to == USER:
            requests.post(f'http://{KIP_ADDRESS}/robot/animations/{KIP_ANIMATION1}')
            requests.post(f'http://{GIMI_ADDRESS}/robot/animations/{KIP_ANIMATION1}')
            requests.post(f'http://{ARM_ADDRESS}/robot/move/{ARM_ANGLE1}')
        elif ball_from == KIP and ball_to == GIMI:
            requests.post(f'http://{KIP_ADDRESS}/robot/animations/{KIP_ANIMATION1}')
            requests.post(f'http://{GIMI_ADDRESS}/robot/animations/{KIP_ANIMATION1}')
            requests.post(f'http://{ARM_ADDRESS}/robot/move/{ARM_ANGLE1}')
        elif ball_from == GIMI and ball_to == USER:
            requests.post(f'http://{KIP_ADDRESS}/robot/animations/{KIP_ANIMATION1}')
            requests.post(f'http://{GIMI_ADDRESS}/robot/animations/{KIP_ANIMATION1}')
            requests.post(f'http://{ARM_ADDRESS}/robot/move/{ARM_ANGLE1}')
        elif ball_from == GIMI and ball_to == KIP:
            requests.post(f'http://{KIP_ADDRESS}/robot/animations/{KIP_ANIMATION1}')
            requests.post(f'http://{GIMI_ADDRESS}/robot/animations/{KIP_ANIMATION1}')
            requests.post(f'http://{ARM_ADDRESS}/robot/move/{ARM_ANGLE1}')
        
        ball_from = ball_to
