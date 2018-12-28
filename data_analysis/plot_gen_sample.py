import os
import argparse
import numpy as np
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument("--data_dir", default="/home/plac/dataset/phos_adc/ds_5/", help="where the dataset is")
parser.add_argument("--index", type=int, default=2, help="which sample to choose")

a = parser.parse_args()

if __name__ == "__main__":
    data_dir = a.data_dir
    index = a.index

    short_file = os.path.join(data_dir, "short", "train", "%08d.bin" % (index))
    long_file = os.path.join(data_dir, "long", "train", "%08d.bin" % (index))

    y_short_noise = np.fromfile(short_file, dtype=np.float32)
    y_long_noise = np.fromfile(long_file, dtype=np.float32)

    print("time label:", y_short_noise[-1])
    y_short_noise = y_short_noise[0:-1]

    assert not len(y_long_noise) % (len(y_short_noise) - 1)
    points = len(y_short_noise)
    super_res = len(y_long_noise) // (len(y_short_noise) - 1)
    print("points:", points, "super_res:", super_res)

    x_short = np.linspace(0, (points-1)*super_res, points, endpoint=True)
    x_long = np.linspace(0, (points-1)*super_res, (points-1)*super_res, endpoint=False)

    assert len(y_short_noise) == len(x_short)
    assert len(y_long_noise) == len(x_long)

    plt.plot(x_short, y_short_noise, "ro")
    plt.plot(x_long, y_long_noise, "b")
    plt.show()
