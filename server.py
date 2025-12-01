import os
import tkinter as tk
import time
import select
class ServerMachine():
    def __init__(self):
        self.state = 'WAITING_REQUEST'
        self.outcoming = "/tmp/pong_pipe"
        self.incoming = "/tmp/ping_pipe"
        self.current_data = None
        self.out_fd = None
        self.in_fd = None
    def setup_pipes(self):
        try:
            os.unlink(self.outcoming)
            os.unlink(self.incoming)
        except FileNotFoundError:
            pass
        os.mkfifo(self.outcoming)
        os.mkfifo(self.incoming)
        print('Каналы созданы, ёпта!')
        print(f'SERVER: State 1.0 ({self.state})')
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
        try:
            os.unlink(self.outcoming)
            os.unlink(self.incoming)
        except FileNotFoundError:
            pass
            print("Ресурсы очищены!")
    def state_one(self):
        if self.in_fd is None:
            try:
                self.in_fd = os.open(self.incoming, os.O_RDONLY | os.O_NONBLOCK)
                self.out_fd = os.open(self.outcoming, os.O_WRONLY)
                print('Клиент подключён!')
            except Exception as e:
                print('Ошибка!')
                return False
        ready, _, _ = select.select([self.in_fd], [], [], None)
        if ready:
            try:
                data = os.read(self.in_fd, 1024)
                if data:
                    self.state = 'CHECKING_REQUEST'
                    self.current_data = data.decode().strip()
                    return True
                else:
                    print('Error!')
                    return False
            except Exception as e:
                print('Ошибка!')
                print(e)
                return False
    def state_two(self):
        print(f'Server: state 2.0 ({self.state})')
        print(f"Received: {self.current_data}")
        self.state = 'SENDING_RESPONSE'
        return True
    def state_three(self):
        
        if self.current_data == 'close':
            print("Сервер остановлен пользователем.")
            return False
        print(f'Server: state 3.0 ({self.state})')
        if self.current_data == 'PING':
            response = 'PONG'
        else:
            response = 'Error command'
        try:
            os.write(self.out_fd, (response + '\n').encode())
            print("Ответ отправлен")
            if response == 'close':
                print('Сервер завершил работу.')
                return False
            self.state = 'WAITING_REQUEST'
            print(f'SERVER: State 1.0 ({self.state})')
        except Exception as e:
            print(f"Ошибка отправки: {e}.")
        return True
    def state_error(self):
        print(f'Ошибка отправки')
        self.cleanup()
        return False
    def run(self):
        self.setup_pipes()
        try:
            while True:
                if self.state == 'WAITING_REQUEST':
                    if not self.state_one(): break
                elif self.state == 'CHECKING_REQUEST':
                    if not self.state_two(): break
                elif self.state == 'SENDING_RESPONSE':
                    if not self.state_three(): break
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nСервер остановлен пользователем")
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
        finally:

            self.cleanup()

def server():
    server_sm = ServerMachine()
    server_sm.run()

if __name__ == "__main__":
    server()
                    
                

       

