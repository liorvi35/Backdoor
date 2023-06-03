from socket import *
import pyautogui
import io


def main():

    with socket(AF_INET, SOCK_STREAM, IPPROTO_TCP) as listening:

        listening.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        listening.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)

        listening.bind(("127.0.0.1", 12345))
        listening.listen(1)

        client, addr = listening.accept()
        with client:

            while True:

                try:

                    screenshot = pyautogui.screenshot()

                    image_buffer = io.BytesIO()
                    screenshot.save(image_buffer, format="PNG")
                    image_data = image_buffer.getvalue()

                    size = len(image_data).to_bytes(4, byteorder="big")
                    client.sendall(size)

                    client.sendall(image_data)

                except KeyboardInterrupt:
                    break

            client.shutdown(SHUT_RDWR)


if __name__ == "__main__":
    main()
