import socket
import time
import queue
import multiprocessing

class Eth():
    def __init__(self, server_addr, server_port):
        self.host = server_addr
        self.port = server_port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.host, self.port))

    def send(self, string, format="h"):
        """ send a string in hex or other format
        """
        if format == "h":
            data = bytes.fromhex(string)
            self.client.send(data)
        else:
            self.client.send(string)

    def recv(self, length=None, to_list=True):
        """ receive and convert it into a list
        """
        if isinstance(length, int):
            data = self.client.recv(length)
        else:
            data = self.client.recv(65536)

        if to_list:
            data = [i for i in data]

        return data

    def close(self):
        self.client.close()

class Eth_hpdaq_adc(Eth):
    def __init__(self, server_addr, server_port, trigger_depth, soft_trigger=True, timeout=None, verbose=1):
        super(Eth_hpdaq_adc, self).__init__(server_addr, server_port)
        self._td = trigger_depth
        self._trigger = soft_trigger
        self._stop = multiprocessing.Event()
        if timeout is None:
            self._timeout = 10
        else:
            self._timeout = timeout
        self._verbose = True if verbose else False

    def init_hpdaq(self):
        # set trigger mode
        if self._trigger: # soft trigger
            self.send("00220001")
        else: # hardware trigger
            self.send("00220000")
        
        # set the start of the ddr storage address
        self.send("00291000")
        self.send("00280000")

        # set trigger depth
        td_init = self._td
        self.send("002b0%03x" % ((td_init & 0x0fff0000) >> 16))
        self.send("002a%04x" % (td_init & 0x0000ffff))

        # start storing data
        self.send("000b0008")

    def run(self, data_queue, trigger_queue=None):
        # initialize
        self.init_hpdaq()
        # main loop
        while not self._stop.is_set():
            if self._trigger:
                if trigger_queue is None:
                    print("configuration error: trigger_queue must be provided in soft trigger mode")
                    return

                # wait for trigger command
                try:
                    trigger_queue.get(timeout=10)
                except queue.Empty:
                    print("software trigger queue timeout occurred in the ethernet module")
                    continue

                # send soft trigger signal
                self.send("000b0010")

            t0 = time.time()
            valid = False
            while time.time() - t0 < self._timeout:
                self.send("80090000")
                data = self.recv(16)
                assert len(data) == 4
                if not (data[2] & 0x10): # valid trigger is detected on hpdaq
                    valid = True
                    break
            if not valid:
                print("trigger waiting time out")
                continue

            # read the address when trigger is detected
            tr_addr = 0
            # high 12 bits
            self.send("80090000")
            data = self.recv(16)
            assert len(data) == 4
            tr_addr += ((data[2] & 0x0f) * 0x100 + data[3]) * 0x10000
            # low 16 bits
            self.send("80080000")
            data = self.recv(16)
            assert len(data) == 4
            tr_addr += data[2] * 0x100 + data[3]

            # set the address where reading starts
            rd_start_addr = tr_addr
            self.send("00270%03x" % ((rd_start_addr & 0x0fff0000) >> 16))
            self.send("0026%04x" % (rd_start_addr & 0x0000ffff))

            # set the address when reading ends
            rd_end_addr = rd_start_addr + self._td
            self.send("002d0%03x" % ((rd_end_addr & 0x0fff0000) >> 16))
            self.send("002c%04x" % (rd_end_addr & 0x0000ffff))

            # set fifo reading length (high 16 bits)
            self.send("001a%04x" % ((self._td & 0xffff0000) >> 16))

            # read ddr to fifo
            self.send("000b0020")

            # set fifo reading length (low 16 bits) and read fifo
            self.send("0019%04x" % (self._td & 0x0000ffff))
            data = self.recv(self._td & 0xffffffff)
            if self._verbose:
                print("receive valid data: %d bytes" % (len(data)))
            data_queue.put(data)

        print("stopping command is sent to ethernet module")
        self.close()
        return

    def stop(self):
        self._stop.set()
