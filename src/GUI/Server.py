    import socket
    import threading
    import io
    from PIL import Image, ImageTk
    from pynput.keyboard import Listener as keyboard
    from pynput.mouse import Listener as mouse
    import tkinter as tk

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


    def video_control() -> None:

        def show_data(image, label) -> None:
            try:
                screenshot_tk = ImageTk.PhotoImage(image)
                label.config(image=screenshot_tk)
                label.image = screenshot_tk  # Store a reference to prevent garbage collection
            except Exception as e:
                pass

        def collect_data() -> None:
            print("Video bound and listening...")
            while True:
                buff = b""
                while True:
                    data, _ = video_server.recvfrom(1024)
                    if data == b"$$$":
                        break
                    buff += data

                screenshot_bytes = io.BytesIO(buff)
                screenshot = Image.open(screenshot_bytes)

                show_data(screenshot, label)

        video_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        video_server.bind((SERVER_IP, SERVER_PORT + 2))

        root = tk.Tk()
        root.geometry("1600x900")

        label = tk.Label()
        label.pack()

        collect = threading.Thread(target=collect_data)
        collect.start()

        root.mainloop()


    if __name__ == "__main__":

        m = threading.Thread(target=mouse_control)
        k = threading.Thread(target=keyboard_control)
        v = threading.Thread(target=video_control)

        m.start()
        k.start()
        v.start()

        m.join()
        k.join()
        v.join()
