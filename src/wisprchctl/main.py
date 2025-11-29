import socket
import sys
import argparse
import os
from importlib.metadata import version, PackageNotFoundError
from wisprch.config import Config

def send_command(command: str) -> str:
    config = Config()
    socket_path = config.socket_path
    
    if not os.path.exists(socket_path):
        print(f"Error: Socket not found at {socket_path}. Is the daemon running?")
        sys.exit(1)
        
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.connect(socket_path)
            client.sendall(command.encode("utf-8"))
            response = client.recv(1024).decode("utf-8")
            return response
    except Exception as e:
        print(f"Error communicating with daemon: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Control wisprch daemon")
    parser.prog = "wisprch"
    
    parser.add_argument("command", choices=["start", "stop", "toggle", "cancel", "status", "help", "version"], help="Command to send")
    
    args = parser.parse_args()
    
    if args.command == "help":
        parser.print_help()
        return

    if args.command == "version":
        try:
            v = version("wisprch")
            print(f"wisprch {v}")
        except PackageNotFoundError:
            print("wisprch (unknown version)")
        return

    response = send_command(args.command)
    print(response)

if __name__ == "__main__":
    main()
