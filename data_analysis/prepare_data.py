import os
import random
import json
import argparse
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate

parser = argparse.ArgumentParser()
parser.add_argument("--raw_dir", required=True, help="where the raw data is")
parser.add_argument("--save_dir", required=True, help="where to save processed data")
parser.add_argument("--total_cnt", type=int, default=120000, help="total files in the raw dataset")
parser.add_argument("--train_cnt", type=int, default=80000, help="training dataset size")
parser.add_argument("--test_cnt", type=int, default=20000, help="test dataset size")
parser.add_argument("--val_cnt", type=int, default=0, help="validation dataset size")

parser.add_argument("--freq", type=int, default=125, help="ADC sampling frequency (MHz)")
parser.add_argument("--start_int", type=int, default=125, help="the interval between trigger and pulse start")
parser.add_argument("--label_rnd", type=int, default=12, help="rounding number for the label")
parser.add_argument("--down_sample", type=int, default=12, help="down sampling rate")
parser.add_argument("--points", type=int, default=33, help="how many points in a sample")
parser.add_argument("--super_res", type=int, default=8, help="super resolution ratio")

a = parser.parse_args()

def read_bin_file(data_file):
    arr = np.fromfile(data_file, dtype=np.int32)
    arr = np.reshape(arr, [4, -1])
    pul = arr[0, :]
    tri = arr[1, :]

    return (pul, tri)

def gen_one_sample(data_file, short_dir, long_dir):
    try:
        pul, tri = read_bin_file(data_file)
    except:
        print("fail to read bin file, exit")
        return -2

    try:
        assert len(pul) == 2048 and len(tri) == 2048
    except:
        print("the length of pulse and trigger is too short:", len(pul))
        return -1

    tri_sel_ind = [e[0] for e in enumerate(tri) if e[1] > 50000]
    if len(tri_sel_ind) == 0:
        print("there are no peaks in the waveform")
        return -1
    elif max(tri_sel_ind) - min(tri_sel_ind) >= 100:
        print("there are two peaks in the waveform")
        return -1

    # get parameters from arguments
    freq = a.freq
    start_int = a.start_int
    label_rnd = a.label_rnd
    down_sample = a.down_sample
    points = a.points
    super_res = a.super_res

    x_trigger = min([e for e in tri_sel_ind if tri[e] == 65535])
    x_start = x_trigger + start_int

    # we decimate the array to 1/12 and set the label
    # original interval: 8 ns, result interval: 96 ns
    actual_start = int(round(x_start / float(label_rnd))) * label_rnd
    label = (x_trigger - actual_start) / freq

    actural_end = actual_start + (points - 1) * down_sample
    x_short = list(range(actual_start, actural_end + down_sample, down_sample))

    # interpolate
    y_short_noise = [pul[e] for e in x_short]
    y_short_noise = np.array(y_short_noise).astype(np.float32) / 24865 + 0.1688
    func = interpolate.interp1d(x_short, y_short_noise, kind="cubic")
    x_long = np.linspace(actual_start, actural_end, (points-1)*super_res, endpoint=False)
    y_long_noise = func(x_long)

    # convert type
    y_short_noise = np.concatenate((y_short_noise, np.array(([label]), dtype=np.float32)), axis=0)
    y_long_noise = np.array(y_long_noise).astype(np.float32)

    # save
    filename = os.path.split(data_file)[-1]
    short_path = os.path.join(short_dir, filename)
    long_path = os.path.join(long_dir, filename)
    y_short_noise.tofile(short_path)
    y_long_noise.tofile(long_path)

    return 0

def generate_data(start_index, perm, raw_dir, short_dir, long_dir, count):
    raw_data_length = len(perm)

    index = start_index
    count_gen = 0
    print("begin from index:", index)
    while count_gen < count:
        if index >= raw_data_length:
            print("finish using raw dataset")
            break
        data_file = os.path.join(raw_dir, "%08d.bin" % (perm[index]+1))
        ret = gen_one_sample(data_file, short_dir, long_dir)
        if ret == -2:
            break
        elif ret == -1:
            index = index + 1
            continue
        else:
            index = index + 1
            count_gen = count_gen + 1

        if not count_gen % 1000:
            print("-------generate %d samples--------" % (count_gen))

    return index


if __name__ == "__main__":
    # get parameters from arguments
    raw_dir = a.raw_dir
    save_dir = a.save_dir
    data_file_count = a.total_cnt
    train_cnt = a.train_cnt
    test_cnt = a.test_cnt
    val_cnt = a.val_cnt

    perm = list(range(data_file_count))
    random.shuffle(perm)

    if os.path.exists(save_dir):
        print("The save directory already exists. Exit.")
        exit(-1)

    os.makedirs(save_dir)

    with open(os.path.join(save_dir, "options.json"), mode="w") as f:
        f.write(json.dumps(vars(a), sort_keys=True, indent=4))
    
    # prepare directories to store the data
    data_paths = {}
    if train_cnt > 0:
        data_paths["short_train"] = os.path.join(save_dir, "short", "train")
        data_paths["long_train"] = os.path.join(save_dir, "long", "train")
    if test_cnt > 0:
        data_paths["short_test"] = os.path.join(save_dir, "short", "test")
        data_paths["long_test"] = os.path.join(save_dir, "long", "test")
    if val_cnt > 0:
        data_paths["short_val"] = os.path.join(save_dir, "short", "val")
        data_paths["long_val"] = os.path.join(save_dir, "long", "val")
    
    # make empty directories
    for value in data_paths.values():
        os.makedirs(value)

    # generate data
    start_index = 0
    if train_cnt > 0:
        start_index = generate_data(start_index, perm, raw_dir, data_paths["short_train"], data_paths["long_train"], train_cnt)
        print("write %d samples to the training set" % (train_cnt))
    if test_cnt > 0:
        start_index = generate_data(start_index, perm, raw_dir, data_paths["short_test"], data_paths["long_test"], test_cnt)
        print("write %d samples to the test set" % (test_cnt))
    if val_cnt > 0:
        _ = generate_data(start_index, perm, raw_dir, data_paths["short_val"], data_paths["long_val"], val_cnt)
        print("write %d samples to the validation set" % (val_cnt))

    print("data generation finished")
