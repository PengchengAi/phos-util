import sys
import os
import argparse
import numpy as np
from scipy import optimize
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument("--input_dir", default="/home/plac/dataset/phos_adc/2019-01-11-11-17-34/", help="input directory")
parser.add_argument("--save_dir", default="")
a = parser.parse_args()

sys.argv = [sys.argv[0]] + ["--input_dir", str(a.input_dir), "--verbose", str(0)]
print(sys.argv)

import trigger_fit_square

tau_p = 0.2672

def pulse(x, K, t_0, base):
    f = lambda t : K * (((t - t_0)/tau_p) ** 2) * np.exp(-2.0 * (t - t_0) / tau_p) + base
    res = np.piecewise(x, [x < t_0, x >= t_0], [base, f])
    return res

def standard_pulse():
    K = 5.12
    t_0 = -0.01
    base = 0.1
    points = 33
    interval = 0.01
    x = np.linspace(0.0, (points-1)*interval, points, endpoint=True)
    y = pulse(x, K, t_0, base)
    print("max value:", max(y))
    plt.plot(x, y, "b")

def read_bin_file(data_file):
    arr = np.fromfile(data_file, dtype=np.int32)
    arr = np.reshape(arr, [4, -1])
    pul = arr[0, :]
    tri = arr[1, :]

    return (pul, tri)

def get_base_amp(start, stop, draw=False):
    input_dir = a.input_dir

    max_list = []
    K_list = []
    t_0_list = []
    base_list = []
    error_cnt = 0
    for ii in range(start, stop):
        data_file = os.path.join(input_dir, "%08d.bin" % (ii + 1))

        # get pulse and trigger signal
        try:
            pul, tri = read_bin_file(data_file)
        except:
            print("file reading ends")
            break

        try:
            assert len(pul) == 2048 and len(tri) == 2048
        except:
            print("the length of pulse and trigger is too short:", len(pul))
            error_cnt = error_cnt + 1
            continue

        tri_sel_ind = [e[0] for e in enumerate(tri) if e[1] > 50000]
        if len(tri_sel_ind) == 0:
            print("there are no peaks in the waveform")
            error_cnt = error_cnt + 1
            continue
        elif max(tri_sel_ind) - min(tri_sel_ind) >= 100:
            print("there are two peaks in the waveform")
            error_cnt = error_cnt + 1
            continue

        # fit the trigger pulse to get the trigger
        ret = trigger_fit_square.tri_process(tri, os.path.basename(data_file), coarse=True)
        if ret is None:
            error_cnt = error_cnt + 1
            continue
        _, refer, _, _ = ret
        x_trigger = refer

        x_start = x_trigger + 25
        x_end = x_trigger + 62

        if x_end >= len(pul):
            print("the end point is out of range")
            error_cnt = error_cnt + 1
            continue

        x = np.arange(0, x_end - x_start)
        x_r = x / 125.0

        y_r = pul[x_start : x_end]
        y_r = np.array(y_r).astype(np.float32) / 36261 + 0.0427

        # maximum pulse value
        max_val = max(y_r)

        # fit the original data
        popt_r, _ = optimize.curve_fit(pulse, x_r, y_r, p0=[1.0, 0.0, 0.0])

        assert len(popt_r) == 3

        K_val = popt_r[0]
        t_0_val = popt_r[1]
        base_val = popt_r[2]

        max_list.append(max_val)
        K_list.append(K_val)
        t_0_list.append(t_0_val)
        base_list.append(base_val)

        if draw:
            y_fit = pulse(x_r, popt_r[0], popt_r[1], popt_r[2])
            plt.plot(x_r, y_r, "r", x_r, y_fit, "g")
            plt.show()

        if K_val < 0:
            print("find abnormal sample:", data_file, "K value:", K_val)

        if not (ii + 1) % 1000:
            print("finish checking %d files" % (ii + 1))

    # print result
    print("error count:", error_cnt)
    print("max value range:", min(max_list), "to", max(max_list))
    print("K value range:", min(K_list), "to", max(K_list))
    print("t_0 value range:", min(t_0_list), "to", max(t_0_list))
    print("base value range:", min(base_list), "to", max(base_list))

    # save result
    save_dir = a.save_dir
    if save_dir != "":
        max_list = np.array(max_list, dtype=np.float32)
        K_list = np.array(K_list, dtype=np.float32)
        t_0_list = np.array(t_0_list, dtype=np.float32)
        base_list = np.array(base_list, dtype=np.float32)

        max_list.tofile(os.path.join(save_dir, "max_list.bin"))
        K_list.tofile(os.path.join(save_dir, "K_list.bin"))
        t_0_list.tofile(os.path.join(save_dir, "t_0_list.bin"))
        base_list.tofile(os.path.join(save_dir, "base_list.bin"))

if __name__ == "__main__":
    get_base_amp(0, 120000, False)
