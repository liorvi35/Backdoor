import socket
import struct
import sys
from PIL import ImageGrab
from pynput import keyboard, mouse

class RemoteSender:
    def __init__(self, server_addr: tuple):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        self.sock.bind(server_addr)
        self.sock.listen(1)

        self.client, addr = self.sock.accept()

        # Mouse event listener
        self.mouse_listener = mouse.Listener(on_move=self.on_mouse_move, on_click=self.on_mouse_click)
        self.mouse_listener.start()

        # Keyboard event listener
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.keyboard_listener.start()

    def close(self):
        self.client.shutdown(socket.SHUT_RDWR)
        self.client.close()
        self.sock.close()

        sys.exit(0)

    def run(self):
        try:
            while True:
                screenshot = ImageGrab.grab()
                screenshot_bytes = screenshot.tobytes()
                screenshot_size = len(screenshot_bytes)
                size_bytes = struct.pack("!I", screenshot_size)

                self.client.sendall(size_bytes)
                self.client.sendall(screenshot_bytes)
        except KeyboardInterrupt:
            self.close()

    def on_mouse_move(self, x, y):
        # Send the mouse coordinates to the client
        mouse_coordinates = f"MOUSE_MOVE: {x}, {y}"
        self.client.sendall(mouse_coordinates.encode())

    def on_mouse_click(self, x, y, button, pressed):
        if pressed:
            # Perform an action based on the mouse button click
            # For example, send the mouse click event to the client
            click_event = f"MOUSE_CLICK: {button} - {x}, {y}"
            self.client.sendall(click_event.encode())

    def on_key_press(self, key):
        try:
            # Get the key value as a string
            key_value = key.char
            # Send the key value to the client
            self.client.sendall(key_value.encode())
        except AttributeError:
            # If the key has no char attribute (e.g., special keys), ignore it
            pass

if __name__ == "__main__":
    sender = RemoteSender(("127.0.0.1", 12345))
    sender.run()
