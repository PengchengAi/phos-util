import os
import numpy as np
import matplotlib.pyplot as plt

data_dir = "/home/plac/dataset/phos_adc/ds_test/"

if __name__ == "__main__":
    index = 810
    short_file = os.path.join(data_dir, "short", "train", "%08d.bin" % (index))
    long_file = os.path.join(data_dir, "long", "train", "%08d.bin" % (index))

    y_short_noise = np.fromfile(short_file, dtype=np.float32)
    y_long_noise = np.fromfile(long_file, dtype=np.float32)

    print("time label:", y_short_noise[33])
    y_short_noise = y_short_noise[0:33]

    points = 33
    super_res = 8

    x_short = np.linspace(0, (points-1)*super_res, points, endpoint=True)
    x_long = np.linspace(0, (points-1)*super_res, (points-1)*super_res, endpoint=False)

    assert len(y_short_noise) == len(x_short)
    assert len(y_long_noise) == len(x_long)

    plt.plot(x_short, y_short_noise, "ro")
    plt.plot(x_long, y_long_noise, "b")
    plt.show()