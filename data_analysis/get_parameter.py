import os
import time
import numpy as np
from scipy import optimize
import matplotlib.pyplot as plt

data_dir = "/home/plac/dataset/phos_adc/2018-12-05-11-38-33/"

tau_p = 2.0

def pulse(x, K, t_0, base):
    f = lambda t : K * (((t - t_0)/tau_p) ** 2) * np.exp(-2.0 * (t - t_0) / tau_p) + base
    res = np.piecewise(x, [x < t_0, x >= t_0], [base, f])
    return res

def standard_pulse():
    K = 5.12
    t_0 = -0.4
    base = 0.1
    points = 33
    interval = 0.1
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
    max_list = []
    K_list = []
    t_0_list = []
    base_list = []
    error_cnt = 0
    for ii in range(start, stop):
        data_file = os.path.join(data_dir, "%08d.bin" % (ii + 1))

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

        x_trigger = min([e for e in tri_sel_ind if tri[e] == 65535])
        x_start = x_trigger + 125
        x_end = x_trigger + 400

        x = np.arange(0, x_end - x_start)
        x_r = x / 125.0

        y_r = pul[x_start : x_end]
        y_r = np.array(y_r).astype(np.float32) / 24865 + 0.1688

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

    # print result
    print("error count:", error_cnt)
    print("max value range:", min(max_list), "to", max(max_list))
    print("K value range:", min(K_list), "to", max(K_list))
    print("t_0 value range:", min(t_0_list), "to", max(t_0_list))
    print("base value range:", min(base_list), "to", max(base_list))


if __name__ == "__main__":
    get_base_amp(0, 120000, False)
