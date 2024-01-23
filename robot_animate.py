### Define animation ###
from typing import Dict, List

class Animation:
    def __init__(
        self,
        id: str,
        positions: Dict[str, List[int]],
        duration,
        ):
        self.id = id
        self.positions = positions
        self.duration = duration
        
    def to_json(self):
        return {
            "id": self.id,
            "positions": self.positions,
            "duration": self.duration,
        }
        
### Define robot ####
from typing import List

class Robot:
    def __init__(
        self,
        id: str,
        deviceName: str,
        baudrate: int,
        motors: List[int],
        animations: List[Animation],
        ):
        self.id = id
        self.deviceName = deviceName
        self.baudrate = baudrate
        self.motors = motors
        self.animations = animations
        
    def to_json(self):
        return {
            "id": self.id,
            "device_name": self.deviceName,
            "baudrate": self.baudrate,
            "motors": self.motors,
            "animations": [animation.to_json() for animation in self.animations],
        }

### Initialize animation #############################################################################

import os
import json

animations = []
animation_folder = "animations/"

for filename in os.listdir(animation_folder):
    if filename.endswith(".json"):
        file_path = os.path.join(animation_folder, filename)
        with open(file_path, "r") as file:
            animation_data = json.load(file)
            animation = Animation(animation_data["id"], animation_data["positions"], animation_data["duration"])
            animations.append(animation)

### Initialize robot ###
import sys
from dynamixel_sdk import *  

id = sys.argv[1]
deviceName = sys.argv[2]

robot = Robot(
    id=id,
    deviceName=deviceName,
    baudrate=57600,
    motors=[1, 2],
    animations=animations,
    )

# Control table address
ADDR_MX_TORQUE_ENABLE      = 24               
ADDR_MX_GOAL_POSITION      = 30
ADDR_MX_PRESENT_POSITION   = 36

# Data Byte Length
LEN_MX_GOAL_POSITION       = 4
LEN_MX_PRESENT_POSITION    = 4

# Protocol version
PROTOCOL_VERSION            = 1.0       

TORQUE_ENABLE               = 1                 # Value for enabling the torque
TORQUE_DISABLE              = 0                 # Value for disabling the torque


# Initialize PortHandler instance
# Set the port path
# Get methods and members of PortHandlerLinux or PortHandlerWindows
global portHandler
portHandler = PortHandler(robot.deviceName)


# Initialize PacketHandler instance
# Set the protocol version
# Get methods and members of Protocol1PacketHandler or Protocol2PacketHandler
global packetHandler
packetHandler = PacketHandler(PROTOCOL_VERSION)

# Initialize GroupSyncWrite instance
global groupSyncWrite
groupSyncWrite = GroupSyncWrite(portHandler, packetHandler, ADDR_MX_GOAL_POSITION, LEN_MX_GOAL_POSITION)

# Open port
if portHandler.openPort():
    print("Succeeded to open the port")
else:
    print("Failed to open the port")
    quit()

# Set port baudrate
if portHandler.setBaudRate(robot.baudrate):
    print("Succeeded to change the baudrate")
else: 
    print("Failed to change the baudrate")
    quit()

# Enable motors torque
for motor in robot.motors:
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, motor, ADDR_MX_TORQUE_ENABLE, TORQUE_ENABLE)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    else:
        print("Dynamixel#%d has been successfully connected" % motor)

### FLASK WEBSERVER ###
from werkzeug.exceptions import HTTPException
import sched, time
from flask import Flask
app = Flask(__name__)

@app.get("/api/robot")
def get_robot():
    return robot.to_json()

@app.get("/api/robot/animations")
def get_animations():
    return [animation.to_json() for animation in robot.animations]

@app.post("/api/robot/animations/<animation_id>")
def animate(animation_id: str):
    animation = next((animation for animation in robot.animations if animation.id == animation_id), None)
    if animation is None:
        raise HTTPException(status_code=404, detail="Animation not found")
    
    n_frames = len(animation.positions[str(1)])
    frame_duration = animation.duration / n_frames  
    my_scheduler = sched.scheduler(time.time, time.sleep)
    
    def write_positions(my_scheduler: sched.scheduler, animation: Animation, index: int):
        if index >= n_frames:
            return
        
        for motor in robot.motors:
            goal_position = animation.positions[str(motor)][index]
            param_goal_position = [DXL_LOBYTE(DXL_LOWORD(goal_position)), DXL_HIBYTE(DXL_LOWORD(goal_position)), DXL_LOBYTE(DXL_HIWORD(goal_position)), DXL_HIBYTE(DXL_HIWORD(goal_position))]
            dxl_addparam_result = groupSyncWrite.addParam(motor, param_goal_position)
            if dxl_addparam_result != True:
                print("[ID:%03d] groupSyncWrite addparam failed" % motor)
                quit()
            if dxl_addparam_result != True:
                print("[ID:%03d] groupSyncWrite addparam failed" % motor)
                quit()
        
        # Syncwrite positions
        dxl_comm_result = groupSyncWrite.txPacket()
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))

        # Clear syncwrite parameter storage
        groupSyncWrite.clearParam()
        
        if index < n_frames:
            my_scheduler.enter(frame_duration, 1, write_positions, argument=(my_scheduler, animation, index+1))
            
        if index == 0:
            my_scheduler.run()
            
    write_positions(my_scheduler, animation, 0) 

    return {"status": "ok"}

if __name__ == '__main__':
    app.run(host='0.0.0.0')

