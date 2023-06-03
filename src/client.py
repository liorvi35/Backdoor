import io
from socket import *
from PIL import ImageTk, Image
import tkinter as tk


def main():
    with socket(AF_INET, SOCK_STREAM, IPPROTO_TCP) as client:
        client.connect(("127.0.0.1", 12345))

        window = tk.Tk()
        window.title("Screen Stream")
        #window.geometry("800x600")

        image_label = tk.Label(window)
        image_label.pack()

        def update_image():
            try:
                size_bytes = client.recv(4)
                size = int.from_bytes(size_bytes, byteorder="big")

                image_bytes = b""
                bytes_received = 0
                while bytes_received < size:
                    data = client.recv(size - bytes_received)
                    if not data:
                        break
                    image_bytes += data
                    bytes_received += len(data)

                image = Image.open(io.BytesIO(image_bytes))
                #image = image.resize((800, 600))

                image_tk = ImageTk.PhotoImage(image)

                image_label.configure(image=image_tk)
                image_label.image = image_tk

                window.after(1, update_image)

            except socket.error as e:
                print(f"Error receiving image: {e}")

        update_image()

        window.mainloop()

        client.shutdown(SHUT_RDWR)


if __name__ == "__main__":
    main()
