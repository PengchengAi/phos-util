import os
import numpy as np
import matplotlib.pyplot as plt

data_dir = "/home/plac/dataset/phos_adc/2018-12-05-11-38-33/"

def show_trigger(data_file):
    arr = np.fromfile(data_file, dtype=np.int32)

    arr = np.reshape(arr, [4, -1])

    y = arr[1, :]

    try:
        assert len(y) == 2048
    except:
        print("the length of trigger is too short")
        return

    y_sel_ind = [e[0] for e in enumerate(y) if e[1] > 50000]
    if len(y_sel_ind) == 0:
        print("there are no peaks in the waveform")
        return
    elif max(y_sel_ind) - min(y_sel_ind) >= 100:
        print("there are two peaks in the waveform")
        return

    x_min = max(min(y_sel_ind) - 15, 0)
    x_max = min(max(y_sel_ind) + 15, 2048)

    y_max = max([y[e] for e in y_sel_ind])
    print("maximum count value:", y_max)

    x = np.arange(x_min, x_max)

    plt.title("file %s" % (os.path.split(data_file)[-1]))
    plt.xlabel("trigger samples")
    plt.ylabel("ADC count value")
    plt.plot(x, y[x_min : x_max], "g", label="trigger signal")
    plt.legend()

    plt.show()

def show_pulse(data_file):
    arr = np.fromfile(data_file, dtype=np.int32)

    arr = np.reshape(arr, [4, -1])

    y = arr[1, :]

    try:
        assert len(y) == 2048
    except:
        print("the length of trigger is too short")
        return

    y_sel_ind = [e[0] for e in enumerate(y) if e[1] > 50000]
    if len(y_sel_ind) == 0:
        print("there are no peaks in the waveform")
        return
    elif max(y_sel_ind) - min(y_sel_ind) >= 100:
        print("there are two peaks in the waveform")
        return

    x_trigger = min([e for e in y_sel_ind if y[e] == 65535])
    x_start = x_trigger + 125
    x_end = x_trigger + 400

    x = np.arange(0, x_end - x_start)

    z = arr[0, :]

    plt.title("file %s" % (os.path.split(data_file)[-1]))
    plt.xlabel("pulse samples")
    plt.ylabel("ADC count value")
    plt.plot(x, z[x_start : x_end], label="trigger signal")
    plt.legend()

    plt.show()

def show_pulse_col(count):
    for ii in range(count):
        data_file = os.path.join(data_dir, "%08d.bin" % (ii + 1))

        arr = np.fromfile(data_file, dtype=np.int32)

        arr = np.reshape(arr, [4, -1])

        y = arr[1, :]

        try:
            assert len(y) == 2048
        except:
            print("the length of trigger is too short")
            continue

        y_sel_ind = [e[0] for e in enumerate(y) if e[1] > 50000]
        if len(y_sel_ind) == 0:
            print("there are no peaks in the waveform")
            continue
        elif max(y_sel_ind) - min(y_sel_ind) >= 100:
            print("there are two peaks in the waveform")
            continue

        x_trigger = min([e for e in y_sel_ind if y[e] == 65535])
        x_start = x_trigger + 125
        x_end = x_trigger + 400

        x = np.arange(0, x_end - x_start)

        z = arr[0, :]

        plt.plot(x, z[x_start : x_end], label="trigger signal")

    plt.title("plot %d files" % count)
    plt.xlabel("pulse samples")
    plt.ylabel("ADC count value")
    plt.show()

if __name__ == "__main__":
    # for ii in range(20):
    #     show_trigger(os.path.join(data_dir, "%08d.bin" % (ii + 1)))
    #     show_pulse(os.path.join(data_dir, "%08d.bin" % (ii + 1)))
    show_pulse_col(20)
