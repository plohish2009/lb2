import os
import threading
import time
import tkinter as tk
from tkinter import ttk
import select


class ClientMachine():
    def window_deleted(self):
        self.root.quit()
        self.state = 'INTERUPTED'
        self.root.destroy()

    def add_close_to_stack(self):
        self.current_request = 'close'
        self.request_pending = False
        self.window_deleted()

    def add_to_stack(self):
        self.current_request = 'PING'
        self.request_pending = True

    def add_message_to_stack(self):
        mesage = self.entry.get()
        if mesage:
            self.entry.delete(0, tk.END)
            self.current_request = mesage
            self.request_pending = True

    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Client')
        self.root.geometry('1200x800+200+0')
        self.root.resizable(False, False)

        PRIMARY = "#4CAF50"
        PRIMARY_HOVER = "#66BB6A"
        PRIMARY_PRESSED = "#388E3C"

        BG_MAIN = "#f0f0f0"
        BG_CONTENT = "#ffffff"
        TEXT_COLOR = "#333333"

        self.root.configure(bg=BG_MAIN)

        default_font = ("Montserrat", 12)
        self.root.option_add("*Font", default_font)

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "App.TButton",
            padding=12,
            background=PRIMARY,
            foreground="white",
            focusthickness=3,
            borderwidth=0,
            borderradius=10
        )

        style.map(
            "App.TButton",
            background=[
                ("active", PRIMARY_HOVER)  
            ]
        )


        

        input_title = tk.Label(
            self.root,
            text="Введите ваше сообщение",
            font=("Montserrat", 14, "bold"),
            bg=BG_MAIN,
            fg=TEXT_COLOR
        )
        input_title.pack(pady=(20, 5))

        input_frame = ttk.Frame(self.root)
        input_frame.pack(pady=10)

        self.entry = ttk.Entry(input_frame, width=80)
        self.entry.pack(side=tk.LEFT, padx=5)

        button_frame = tk.Frame(self.root, bg=BG_MAIN)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)

        def make_button(parent, text, cmd):
            btn = ttk.Button(parent, text=text, command=cmd, style="App.TButton")
            btn.pack(side=tk.LEFT, expand=True, padx=10)
            return btn

        self.Button_Add = make_button(button_frame, "SEND COMMAND", self.add_message_to_stack)
        self.Button_Clear = make_button(button_frame, "Clear", self.clear_history)
        self.Button_Ping = make_button(button_frame, "Ping", self.add_to_stack)
        self.Button_Quit = make_button(button_frame, "Close", self.add_close_to_stack)

        # ---------- MAIN CONTENT ----------
        content_frame = tk.Frame(
            self.root, bg=BG_CONTENT, relief=tk.SUNKEN, bd=1
        )
        content_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        history_title = tk.Label(
            content_frame,
            text="История обмена сообщениями:",
            font=('Montserrat', 14, 'bold'),
            bg=BG_CONTENT,
            fg=TEXT_COLOR
        )
        history_title.pack(pady=(10, 5))

        text_frame = tk.Frame(content_frame, bg=BG_CONTENT)
        text_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

        self.text_widget = tk.Text(
            text_frame,
            font=('Montserrat', 11),
            bg="#f8f8f8",
            fg=TEXT_COLOR,
            wrap=tk.WORD,
            height=15,
            state=tk.DISABLED
        )
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(text_frame, command=self.text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_widget.config(yscrollcommand=scrollbar.set)

        # Цветовые теги
        self.text_widget.tag_configure("timestamp", foreground="#666666")
        self.text_widget.tag_configure("info", foreground="#333333")
        self.text_widget.tag_configure("sent", foreground="#2E7D32")
        self.text_widget.tag_configure("received", foreground="#1565C0")
        self.text_widget.tag_configure("error", foreground="#C62828")

        title_label = tk.Label(
            content_frame,
            text="Client Application",
            font=('Montserrat', 16, 'bold'),
            bg=BG_CONTENT,
            fg=TEXT_COLOR
        )
        title_label.pack(pady=20)

        # ---------- STATE MACHINE ----------
        self.root.protocol('WM_DELETE_WINDOW', self.window_deleted)

        self.state = 'CREATING_REQUEST'
        self.current_request = None
        self.request_pending = False

        self.outcoming = "/tmp/ping_pipe"
        self.incoming = "/tmp/pong_pipe"
        self.out_fd = None
        self.in_fd = None

    def add_message(self, message, message_type="info"):
        timestamp = time.strftime("%H:%M:%S")

        self.text_widget.config(state=tk.NORMAL)

        self.text_widget.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.text_widget.insert(tk.END, f"{message}\n", message_type)

        self.text_widget.config(state=tk.DISABLED)
        self.text_widget.see(tk.END)

    def clear_history(self):
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.config(state=tk.DISABLED)

    def cleanup(self):
        if self.in_fd:
            try:
                os.close(self.in_fd)
            except OSError:
                pass
        if self.out_fd:
            try:
                os.close(self.out_fd)
            except OSError:
                pass

    def connect_to_server(self):
        try:
            self.out_fd = os.open(self.outcoming, os.O_WRONLY)
            self.in_fd = os.open(self.incoming, os.O_RDONLY | os.O_NONBLOCK)
            return True
        except FileNotFoundError:
            print('Не удалось подключиться к серверу!')
            return False

    def state_one(self):
        if not self.request_pending:
            return True
        self.add_message(f'Client: state 1.0 ({self.state})')

        try:
            os.write(self.out_fd, (self.current_request + '\n').encode())
            self.add_message("Сообщение отправлено!", "sent")
            self.state = 'WAITING_FOR_ANSWER'
            self.request_pending = False
            if self.current_request == 'close':
                return False
        except Exception as e:
            print(f"Ошибка отправки: {e}")
            return False
        return True

    def state_two(self):
        self.add_message(f'Client: state 2.0 ({self.state})')
        start = time.time()

        while time.time() - start < 200:
            ready, _, _ = select.select([self.in_fd], [], [], 1.0)
            if ready:
                self.state = "READING_RESPONSE"
                return True

        return False

    def state_three(self):
        try:
            data = os.read(self.in_fd, 1024)
            response = data.decode().strip()

            self.add_message(f'Ответ получен! Вы получили: {response}', "received")

            if response == 'close':
                return False

            self.state = "CREATING_REQUEST"
        except Exception as e:
            print(f"Ошибка чтения: {e}")
            return False

        return True

    def run(self):
        self.add_message("Клиент запускается...", "info")

        if not self.connect_to_server():
            self.add_message("не удалось подключиться к серверу", "error")
            self.cleanup()
            self.window_deleted()
            return

        try:
            while True:
                if self.state == "CREATING_REQUEST":
                    if not self.state_one(): break

                elif self.state == "WAITING_FOR_ANSWER":
                    if not self.state_two(): break

                elif self.state == "READING_RESPONSE":
                    if not self.state_three(): break

                if self.state == 'INTERUPTED':
                    break

                time.sleep(0.5)

        finally:
            self.cleanup()
            self.window_deleted()


def client():
    client_sm = ClientMachine()
    client_thread = threading.Thread(target=client_sm.run, daemon=True)
    client_thread.start()
    client_sm.root.mainloop()


if __name__ == "__main__":
    client()
