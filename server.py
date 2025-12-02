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
        print('Pipes were created!')
        print('Waiting for connection with client...')

        # print(f'SERVER: State 1.0 ({self.state})')

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
            print("Sources are cleared!")

    def state_one(self):
        if self.in_fd is None:
            try:
                self.in_fd = os.open(self.incoming, os.O_RDONLY | os.O_NONBLOCK)
                self.out_fd = os.open(self.outcoming, os.O_WRONLY)
                print('Client is connected!')
            except Exception as e:
                print('Error!')
                return False
        print(f'SERVER: State 1.0 ({self.state})')
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
                print('Error!')
                print(e)
                return False

    def state_two(self):
        print(f'Server: state 2.0 ({self.state})')
        print(f"Received: {self.current_data}")
        self.state = 'SENDING_RESPONSE'
        return True

    def state_three(self):

        if self.current_data == 'close':
            print("Server was stopped by client.")
            return False
        print(f'Server: state 3.0 ({self.state})')
        if self.current_data.upper() == 'PING':
            response = 'PONG'
        else:
            response = 'Error command'
        try:
            os.write(self.out_fd, (response + '\n').encode())
            print("Response was sent")
            self.state = 'WAITING_REQUEST'
        except Exception as e:
            print(f"Error of sending: {e}.")
        return True

    def state_error(self):
        print(f'Error of sending')
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
            print("\nServer was stopped by client")
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:

            self.cleanup()


def server():
    server_sm = ServerMachine()
    server_sm.run()


if __name__ == "__main__":
    server()



