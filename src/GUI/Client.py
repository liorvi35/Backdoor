import socket
import threading
from pynput.keyboard import Controller as keyboard_ctrl, Key
from pynput.mouse import Controller as mouse_ctrl, Button

SERVER_IP = "10.0.0.13"
SERVER_PORT = 3000

button_map = {
    "Button.left": Button.left,
    "Button.right": Button.right,
    "Button.middle": Button.middle,
}

key_map = {
    "Key.ctrl": Key.ctrl,
    "Key.ctrl_r": Key.ctrl_r,
    "Key.alt": Key.alt,
    "Key.alt_r": Key.alt_r,
    "Key.shift": Key.shift,
    "Key.shift_r": Key.shift_r,
    "Key.esc": Key.esc,
    "Key.backspace": Key.backspace,
    "Key.left": Key.left,
    "Key.right": Key.right,
    "Key.up": Key.up,
    "Key.down": Key.down,
    "Key.delete": Key.delete,
    "Key.cmd": Key.cmd,
    "Key.space": Key.space,
    "Key.enter": Key.enter,
    "Key.f1": Key.f1,
    "Key.f2": Key.f2,
    "Key.f3": Key.f3,
    "Key.f4": Key.f4,
    "Key.f5": Key.f5,
    "Key.f6": Key.f6,
    "Key.f7": Key.f7,
    "Key.f8": Key.f8,
    "Key.f9": Key.f9,
    "Key.f10": Key.f10,
    "Key.f11": Key.f11,
    "Key.f12": Key.f12,
    "Key.f13": Key.f13,
    "Key.f14": Key.f14,
    "Key.f15": Key.f15,
    "Key.f16": Key.f16,
    "Key.f17": Key.f17,
    "Key.f18": Key.f18,
    "Key.f19": Key.f19,
    "Key.f20": Key.f20,
    "Key.tab": Key.tab
}


def get_control_mouse() -> None:
    def get_move(x, y) -> None:
        mouse.position = (x, y)

    def get_click(button) -> None:
        if button != "Button.Unknown":
            mouse.click(button_map[button])

    def get_scroll(dx, dy) -> None:
        mouse.scroll(int(dx), int(dy))

    mouse = mouse_ctrl()

    mouse_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    mouse_client.sendto("$".encode(), (SERVER_IP, SERVER_PORT))

    while True:
        cmd, _ = mouse_client.recvfrom(1024)
        cmd = cmd.decode()

        args = cmd.split(",")

        if args[0] == "MOVE":
            get_move(args[1], args[2])
        elif args[0] == "CLICK":
            get_click(args[1])
        elif args[0] == "SCROLL":
            get_scroll(args[1], args[2])


def get_control_keyboard() -> None:

    def get_press(key) -> None:
        try:
            keyboard.press(key)
        except ValueError:
            keyboard.press(key_map[key])

    def get_release(key) -> None:
        try:
            keyboard.release(key)
        except ValueError:
            keyboard.release(key_map[key])

    keyboard = keyboard_ctrl()

    keyboard_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    keyboard_client.sendto("@".encode(), (SERVER_IP, SERVER_PORT + 1))

    while True:
        cmd, _ = keyboard_client.recvfrom(1024)
        cmd = cmd.decode()

        args = cmd.split(",")

        print(args)

        if args[0] == "PRESS":
            get_press(args[1].strip("'"))
        elif args[0] == "RELEASE":
            get_release(args[1].strip("'"))


if __name__ == "__main__":
    m = threading.Thread(target=get_control_mouse)
    k = threading.Thread(target=get_control_keyboard)

    m.start()
    k.start()

    m.join()
    k.join()
