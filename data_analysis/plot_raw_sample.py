import os
import numpy as np
import matplotlib.pyplot as plt

data_dir = "/home/plac/dataset/phos_adc/2018-12-05-11-38-33/"

if __name__ == "__main__":
    data_file = os.path.join(data_dir, "00000002.bin")

    arr = np.fromfile(data_file, dtype=np.int32)

    arr = np.reshape(arr, [4, -1])

    x = np.arange(0, arr.shape[1])

    x = x / 125

    plt.xlabel(r"time ($\mu$s)")
    plt.ylabel("ADC count value")
    plt.plot(x, arr[0, :], "r", label="PHOS FEE pulse")
    plt.plot(x, arr[1, :], "g", label="trigger signal")
    plt.legend()

    plt.show()
