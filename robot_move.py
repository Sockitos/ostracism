### Define robot ####
from typing import List

class Robot:
    def __init__(
        self,
        id: str,
        deviceName: str,
        baudrate: int,
        motor: int,
        ):
        self.id = id
        self.deviceName = deviceName
        self.baudrate = baudrate
        self.motor = motor
        
    def to_json(self):
        return {
            "id": self.id,
            "device_name": self.deviceName,
            "baudrate": self.baudrate,
            "motor": self.motor,
        }

### Initialize robot ###
import sys
from dynamixel_sdk import *  

id = sys.argv[1]
deviceName = sys.argv[2]

robot = Robot(
    id=id,
    deviceName=deviceName,
    baudrate=57600,
    motor=1,
    )

# Control table address
ADDR_MX_TORQUE_ENABLE      = 64               
ADDR_MX_GOAL_POSITION      = 116

# Address for velocity control
ADDR_MX_PROFILE_VELOCITY = 112

ADDR_OPERATING_MODE = 11

# Data Byte Length
LEN_MX_GOAL_POSITION       = 4
LEN_MX_PRESENT_POSITION    = 4

# Protocol version
PROTOCOL_VERSION            = 2.0       

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

    
dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, robot.motor, ADDR_MX_TORQUE_ENABLE, TORQUE_ENABLE)
if dxl_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    print("%s" % packetHandler.getRxPacketError(dxl_error))
else:
    print("Dynamixel#%d has been successfully connected" % robot.motor)

profile_velocity  = 15

dxl_comm_result_velocity, dxl_error_velocity = packetHandler.write4ByteTxRx(portHandler, robot.motor, ADDR_MX_PROFILE_VELOCITY, profile_velocity)

# Multi Turn Mode 
dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, robot.motor, ADDR_OPERATING_MODE, 4)
if dxl_comm_result != COMM_SUCCESS:
    print(f"Error mode control: {packetHandler.getTxRxResult(dxl_comm_result)}")
    quit()

    
### FLASK WEBSERVER ###
from flask import Flask, request
app = Flask(__name__)

@app.get("/api/robot")
def get_robot():
    return robot.to_json()

@app.post("/api/robot/move/<angle>")
def move(angle: int):
    current_position, _, _ = packetHandler.read4ByteTxRx(portHandler, robot.motor, ADDR_MX_GOAL_POSITION)
    goal_position = current_position + int((int(angle)/ 360) * 4096)
     
    # Write goal position 
    dxl_comm_result_position, dxl_error_position = packetHandler.write4ByteTxRx(portHandler, robot.motor, ADDR_MX_GOAL_POSITION, goal_position)
    print(goal_position)
    if dxl_comm_result_position != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result_position))
    elif dxl_error_position != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error_position))

    return {"status": "ok"}

if __name__ == '__main__':
    app.run(host='0.0.0.0')

