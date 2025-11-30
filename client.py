import os
import threading
import time
import tkinter as tk
import select
class ClientMachine():
    def window_deleted(self):
        self.root.quit()
        self.state = 'INTERUPTED'
        self.root.destroy()
    def add_close_to_stack(self):
        self.stack.append('close')
        self.window_deleted()
    def add_to_stack(self):
        self.stack.append('PING')
    def add_message_to_stack(self):
        mesage = self.entry.get()
        if mesage:
            self.entry.delete(0, tk.END) 
            self.stack.append(mesage)
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Client')
        self.root.geometry('1200x800+200+0')
        self.root.resizable(False, False)
        self.root.configure(bg='#f0f0f0')  # Светлый фон
        self.entry = tk.Entry(self.root)
        #self.entry.pack(side=tk.LEFT, padx=400)
        input_frame = tk.Frame(self.root, bg='#f0f0f0')
        input_frame.pack(pady=10)
        self.entry.pack(side=tk.LEFT, padx=5)
        
        # Стили для кнопок
        button_style = {
            'font': ('Arial', 12, 'bold'),
            'bg': '#4CAF50',  # Зеленый цвет
            'fg': 'white',
            'relief': tk.RAISED,
            'bd': 3,
            'width': 12,
            'height': 2
        }
        clear_button_style = button_style.copy()
        clear_button_style['bg'] = "#AF4C7D"
        
        quit_button_style = button_style.copy()
        quit_button_style['bg'] = '#f44336'  # Красный цвет для кнопки выхода
        
        # Создание фрейма для кнопок (для лучшего управления)
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)
        
        self.Button_Add = tk.Button(button_frame, background= '#F4A460', font=('Arial', 12, 'bold'), fg='white', bd=3, width=12, height=2, text='SEND COMMAND', command= self.add_message_to_stack)
        self.Button_Add.pack(side=tk.LEFT, expand=True)
        self.Button_Clear = tk.Button(
        button_frame, 
        text='Clear', 
        command=self.clear_history,
        **clear_button_style
        )
        #self.Button_Clear.pack(side=tk.LEFT, padx=50)
        self.Button_Clear.pack(side=tk.LEFT, expand=True) 
        # Кнопка Ping - слева
        self.Button_Ping = tk.Button(
            button_frame, 
            text='Ping', 
            command=self.add_to_stack,
            **button_style
        )
        #self.Button_Ping.pack(side=tk.LEFT, padx=300)
        self.Button_Ping.pack(side=tk.LEFT, expand=True)
        # Кнопка Quit - справа
        self.Button_Quit = tk.Button(
            button_frame, 
            text='Close', 
            command=self.add_close_to_stack,
            **quit_button_style
        )
        #self.Button_Quit.pack(side=tk.RIGHT, padx=50)
        self.Button_Quit.pack(side=tk.LEFT, expand=True)
        # Центральная область для контента (если нужно)
        content_frame = tk.Frame(self.root, bg='white', relief=tk.SUNKEN, bd=2)
        content_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        
        # Заголовок для истории
        history_title = tk.Label(
            content_frame,
            text="История обмена сообщениями:",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg='#333333'
        )
        history_title.pack(pady=(10, 5))

        # Текстовое поле с прокруткой
        text_frame = tk.Frame(content_frame, bg='white')
        text_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

        self.text_widget = tk.Text(
            text_frame,
            font=('Arial', 11),
            bg='#f8f8f8',
            fg='#333333',
            wrap=tk.WORD,
            height=15,
            state=tk.DISABLED  # Запрещаем прямое редактирование пользователем
        )
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Scrollbar для текстового поля
        scrollbar = tk.Scrollbar(text_frame, command=self.text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_widget.config(yscrollcommand=scrollbar.set)
        # Настраиваем теги для цветов
        self.text_widget.tag_configure("timestamp", foreground="#666666", font=('Arial', 10))
        self.text_widget.tag_configure("info", foreground="#333333")
        self.text_widget.tag_configure("sent", foreground="#2E7D32")
        self.text_widget.tag_configure("received", foreground="#1565C0")
        self.text_widget.tag_configure("error", foreground="#C62828")
            
        # Заголовок или другое содержимое
        title_label = tk.Label(
            content_frame, 
            text="Client Application", 
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#333333'
        )
        title_label.pack(pady=20)
        
        self.root.protocol('WM_DELETE_WINDOW', self.window_deleted)

                
        #self.running = True
        self.state = 'CREATING_REQUEST'
        self.stack = []
        
        self.outcoming = "/tmp/ping_pipe"
        self.incoming = "/tmp/pong_pipe"
        self.out_fd = None
        self.in_fd = None
    # Методы для работы с текстом
    def add_message(self, message, message_type="info"):
        colors = {
            "info": "#333333",
            "sent": "#2E7D32",  # Зеленый для отправленных
            "received": "#1565C0",  # Синий для полученных
            "error": "#C62828"  # Красный для ошибок
        }
        
        self.text_widget.config(state=tk.NORMAL)  # Включаем редактирование
        
        # Добавляем временную метку
        timestamp = time.strftime("%H:%M:%S")
        self.text_widget.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # Добавляем сообщение с цветом
        self.text_widget.insert(tk.END, f"{message}\n", message_type)
        
        self.text_widget.config(state=tk.DISABLED)  # Выключаем редактирование
        self.text_widget.see(tk.END)  # Прокручиваем к концу

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
        #print(f'Client: state 1.0 ({self.state})')
        self.add_message(f'Client: state 1.0 ({self.state})')
        #response = self.entry.get()
        while len(self.stack) == 0:
            time.sleep(0.2)
        response = self.stack.pop()
        try:
            os.write(self.out_fd, (response + '\n').encode())
            self.add_message("Сообщение отправлено!")
            self.state = 'WAITING_FOR_ANSWER'
            if response == 'close':
                print("Клиент завершил работу")
                return False
        except Exception as e:
            print(f"Ошибка отправки: {e}")
            self.state = "ERROR"
            #return False
        return True
    def state_two(self):
        self.add_message(f'Client: state 2.0 ({self.state})')
        start = time.time()
        while time.time() - start < 200:
            ready, _, _ = select.select([self.in_fd], [], [], 1.0)
            if ready:
                self.state = "READING_RESPONSE"
                print('We got something!')
                return True
        return False
    def state_three(self):
        print(f'Client: state 3.0 ({self.state})')
        try:
            data = os.read(self.in_fd, 1024)
            response = data.decode().strip()
            self.add_message(f'Ответ получен! Вы получили: {response}')
            if response == 'close':
                print('Сервер завершил сеанс.')
                return False              
            self.state = "CREATING_REQUEST"
        # except BlockingIOError:
        #     print("Данные недоступны при чтении")
        #     self.state = "WAITING_RESPONSE"
        except Exception as e:
            print(f"Ошибка чтения: {e}")
            return False
        return True
    def run(self):
        self.add_message("Клиент запускается...")
        if not self.connect_to_server():
            self.add_message('не удалось подключиться к серверу')
            self.cleanup()
            self.window_deleted()
            return
        try:
            while True:
                if self.state == "CREATING_REQUEST":
                    if not self.state_one():
                        break
                elif self.state == "WAITING_FOR_ANSWER":
                    if not self.state_two():
                        break
                
                elif self.state == "READING_RESPONSE":
                    if not self.state_three():
                        break
                if self.state == 'INTERUPTED':
                    break
                
                time.sleep(0.5)  # Пауза между итерациями
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
        finally:
            self.cleanup()
            self.window_deleted()
def client():
    client_sm = ClientMachine()
    # Запускаем логику клиента в отдельном потоке
    client_thread = threading.Thread(target=client_sm.run, daemon=True)
    client_thread.start()
    # Запускаем главный цикл Tkinter
    client_sm.root.mainloop()

if __name__ == "__main__":
    client()
