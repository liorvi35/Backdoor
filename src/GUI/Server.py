import socket
import threading
from pynput.keyboard import Listener as keyboard
from pynput.mouse import Listener as mouse

SERVER_IP = "10.0.0.13"
SERVER_PORT = 3000


def mouse_control() -> None:
    def move(x, y) -> None:
        cmd = f"MOVE,{x},{y}".encode()
        mouse_server.sendto(cmd, mouse_client)

    def click(x, y, button, pressed) -> None:
        if pressed:
            cmd = f"CLICK,{button}".encode()
            mouse_server.sendto(cmd, mouse_client)

    def scroll(x, y, dx, dy) -> None:
        cmd = f"SCROLL,{dx},{dy}".encode()
        mouse_server.sendto(cmd, mouse_client)

    mouse_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    mouse_server.bind((SERVER_IP, SERVER_PORT))
    print("Mouse bound and listening...")

    _, mouse_client = mouse_server.recvfrom(1)
    print("Mouse connected!")

    with mouse(on_move=move, on_click=click, on_scroll=scroll) as my_mouse:
        my_mouse.join()


def keyboard_control() -> None:
    def press(key) -> None:
        cmd = f"PRESS,{key}".encode()
        keyboard_server.sendto(cmd, keyboard_client)

    def release(key) -> None:
        cmd = f"RELEASE,{key}".encode()
        keyboard_server.sendto(cmd, keyboard_client)

    keyboard_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    keyboard_server.bind((SERVER_IP, SERVER_PORT + 1))
    print("Keyboard bound and listening...")

    _, keyboard_client = keyboard_server.recvfrom(1)
    print("Keyboard connected!")

    with keyboard(on_press=press, on_release=release) as my_keyboard:
        my_keyboard.join()


if __name__ == "__main__":
    m = threading.Thread(target=mouse_control)
    k = threading.Thread(target=keyboard_control)

    m.start()
    k.start()

    m.join()
    k.join()
