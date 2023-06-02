import socket
import struct
import sys
import tkinter as tk
from PIL import Image, ImageTk
from pynput import keyboard, mouse

class RemoteReceiver:
    def __init__(self, server_addr: tuple):
        self.root = tk.Tk()
        self.root.title(f"{server_addr[0]}:{server_addr[1]}")

        self.label = tk.Label(self.root)
        self.label.pack()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        self.sock.connect(server_addr)

        self.root.withdraw()

        # Mouse event listener
        self.mouse_listener = mouse.Listener(on_move=self.on_mouse_move, on_click=self.on_mouse_click)
        self.mouse_listener.start()

        # Keyboard event listener
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.keyboard_listener.start()

    def close(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        self.root.destroy()

        sys.exit(0)

    def display_screenshot(self, image):
        img_tk = ImageTk.PhotoImage(image)
        self.label.config(image=img_tk)
        self.label.image = img_tk

    def run(self):
        try:
            self.root.deiconify()
            while True:
                size_bytes = self.sock.recv(4)
                screenshot_size = struct.unpack("!I", size_bytes)[0]

                remaining_bytes = screenshot_size
                screenshot_bytes = b""
                while remaining_bytes > 0:
                    received_bytes = self.sock.recv(remaining_bytes)
                    screenshot_bytes += received_bytes
                    remaining_bytes -= len(received_bytes)

                screenshot = Image.frombytes("RGB", (1920, 1080), screenshot_bytes)
                self.display_screenshot(screenshot)
                self.root.update()
        except KeyboardInterrupt:
            self.close()

    def on_mouse_move(self, x, y):
        # Move the mouse on the receiver side
        mouse_controller = mouse.Controller()
        mouse_controller.position = (x, y)

    def on_mouse_click(self, x, y, button, pressed):
        # Perform mouse click on the receiver side
        mouse_controller = mouse.Controller()
        if pressed:
            mouse_controller.press(button)
        else:
            mouse_controller.release(button)

    def on_key_press(self, key):
        # Press the key on the receiver side
        keyboard_controller = keyboard.Controller()
        try:
            # Get the key value as a string
            key_value = key.char
            # Press the key
            keyboard_controller.press(key_value)
            # Release the key
            keyboard_controller.release(key_value)
        except AttributeError:
            # If the key has no char attribute (e.g., special keys), ignore it
            pass

if __name__ == "__main__":
    receiver = RemoteReceiver(("127.0.0.1", 12345))
    receiver.run()
