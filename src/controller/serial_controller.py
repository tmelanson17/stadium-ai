
# Takes in one of two actions: switch or move.
# If switch, it will switch the active mon to the one specified (0-POKEMON_TEAM).
# If move, it will use the move specified (0-3) on the active mon.
# This is converted to a set of commands to send to the controller via serial port.
from typing import Dict, Optional, Tuple
import serial
import time

from src.controller.controller_node import Controller

# Controller maps to the option of the specified index.
_CHARACTER_MAP = [
    '^',
    '>',
    'V',
    '<', 
    'A',
    'B',
]

class SerialController(Controller):
    def __init__(self, port: str, baudrate: int = 9600):
        """
        Initialize the SerialController with the specified serial port.
        
        Args:
            port: The serial port to connect to (e.g., 'COM3' on Windows or '/dev/ttyUSB0' on Linux)
        """
        self.port = port
        self.serial_connection: serial.Serial = serial.Serial(port, baudrate=baudrate, timeout=1)
        time.sleep(1)
        self.serial_connection.flush()  # Clear any existing data in the buffer
        # Begin serial communication
        
        # Initialize serial connection here (omitted for brevity)
    
    def send_command(self, command: str) -> None:
        """
        Send a command to the serial port.
        
        Args:
            command: The command string to send
        """
        command_list = command.strip().split()
        if len(command_list) != 2:
            raise ValueError("Command must be <action> <index>.")
        action, index = command_list
        if action not in ["switch", "move"]:
            raise ValueError("Action must be 'switch' or 'move'.")
        if not index.isdigit() or int(index) < 0:
            raise ValueError("Index must be a non-negative integer.")
        controller_action = "B" if action == "switch" else "A"
        self.serial_connection.write(controller_action.encode('utf-8'))
        self.serial_connection.flush()  # Ensure the command is sent immediately
        time.sleep(0.1)  # Wait for the controller to process the command
        print(self.serial_connection.read(1))  # Read response from controller
        self.serial_connection.write(_CHARACTER_MAP[int(index)].encode('utf-8'))
        self.serial_connection.flush()  # Ensure the command is sent immediately
        time.sleep(0.1)  # Wait for the controller to process the command
        print(self.serial_connection.read(1))  # Read response from controller

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Send commands to a serial controller.")
    parser.add_argument("--port", type=str, help="Serial port to connect to (e.g., 'COM3' or '/dev/ttyUSB0')")
    parser.add_argument("--command", type=str, help="Command to send (e.g., 'switch 1' or 'move 2')")
    parser.add_argument("--random", action="store_true", help="Use random command instead of specified command")
    args = parser.parse_args()

    controller = SerialController(args.port, 9600)
    if args.random:
        import random
        while True:
            action = random.choice(["switch", "move"])
            index = random.randint(0, 3)  # Assuming 4 options for moves or switches
            args.command = f"{action} {index}"
            controller.send_command(args.command)
            print(f"Sent command: {args.command} to port {args.port}")
            time.sleep(10.0)
    else:
        controller.send_command(args.command)
        print(f"Sent command: {args.command} to port {args.port}")