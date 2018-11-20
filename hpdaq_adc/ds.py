import os
import time
import json
import numpy as np
import matplotlib.pyplot as plt

class DS_hpdaq_adc():
    def __init__(self, savedir, conf, max_sample=1000000, dis_interval=0):
        self._savedir = savedir
        self._conf = conf
        self._max_sample = max_sample
        self._dis_interval = dis_interval
        self._stop = False

        if max_sample > 1000000:
            self._max_sample = 1000000

        if dis_interval > 0:
            plt.show()

    def display(self, channels):
        color = ["r", "g", "b", "m"]
        plt.cla()
        x = list(range(len(channels[0])))
        for i in range(4):
            plt.plot(x, channels[i], color=color[i])
        plt.pause(0.00001)

    def makedir(self):
        time_string = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        path = os.path.join(self._savedir, time_string)

        # if dir exists, wait for 1s
        while os.path.exists(path):
            time.sleep(1)
            time_string = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
            path = os.path.join(self._savedir, time_string)
        
        # make the dir
        os.makedirs(path)
        self._dir = path

        # write configurations
        conf_file = os.path.join(path, "conf.json")
        with open(conf_file, "w") as outfile:
            json.dump(self._conf, outfile, indent=4)

    def run(self, data_queue):
        initial_data = True
        ii = 0
        while not self._stop:
            ii = ii + 1
            data = data_queue.get()
            if initial_data:
                self.makedir()
                initial_data = False
            assert not len(data) % 4
            
            # split channels
            cnt = len(data) // 4
            ch0 = [data[i*4] for i in range(cnt)]
            ch1 = [data[i*4+1] for i in range(cnt)]
            ch2 = [data[i*4+2] for i in range(cnt)]
            ch3 = [data[i*4+3] for i in range(cnt)]

            # display channel data (optional)
            if self._dis_interval > 0 and (not (ii % self._dis_interval)):
                self.display([ch0, ch1, ch2, ch3])

            # save to raw data file
            data = np.array([ch0, ch1, ch2, ch3], dtype=np.int32)
            filepath = os.path.join(self._dir, "%08d.bin" % (ii))
            data.tofile(filepath)

            # exit if maximum is reached
            if ii >= self._max_sample:
                print("maximum sample count is reached")
                return

    def stop(self):
        self._stop = True