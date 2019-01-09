import os
import argparse
import numpy as np
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument("--input_dir", required=True, help="input directory")
parser.add_argument("--file_cnt", type=int, default=1000, help="file count")

a = parser.parse_args()

def read_bin_file(data_file):
    arr = np.fromfile(data_file, dtype=np.int32)
    arr = np.reshape(arr, [4, -1])
    pul = arr[0, :]
    tri = arr[1, :]

    return (pul, tri)

def display_data(pul, tri, title):
    assert len(pul) == len(tri)

    x = list(range(len(pul)))
    plt.clf()
    plt.title(title)
    plt.plot(x, pul, "r")
    plt.plot(x, tri, "g")
    plt.show()

if __name__ == "__main__":
    input_dir = a.input_dir
    file_cnt = a.file_cnt

    if not os.path.exists(input_dir):
        print("Input directory does not exist. Exit.")
        exit(-1)

    for i in range(file_cnt):
        fn = "%08d.bin" % (i+1)
        fn = os.path.join(input_dir, fn)
        pul, tri = read_bin_file(fn)
        display_data(pul, tri, os.path.basename(fn))

    print("Finish")

