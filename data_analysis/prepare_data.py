import os
import random
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate

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

    x_trigger = min([e for e in tri_sel_ind if tri[e] == 65535])
    x_start = x_trigger + 125

    # we decimate the array to 1/12 and set the label
    # original interval: 8 ns, result interval: 96 ns
    actual_start = int(round(x_start / 12.0)) * 12
    label = (x_trigger - actual_start) / 125

    actural_end = actual_start + (points - 1) * 12
    x_short = list(range(actual_start, actural_end + 12, 12))

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
    while count_gen < count:
        if index >= raw_data_length:
            print("finish using raw dataset")
            break
        data_file = os.path.join(raw_dir, "%08d.bin", perm[index]+1)
        ret = gen_one_sample(data_file, short_dir, long_dir)
        if ret == -2:
            break
        elif ret == -1:
            continue
        else:
            index = index + 1
            count_gen = count_gen + 1

        if not count_gen % 1000:
            print("-------generate %d samples--------" % (count_gen))

    return index


if __name__ == "__main__":
    raw_dir = "/home/plac/dataset/phos_adc/2018-12-05-11-38-33/"
    save_dir = "/home/plac/dataset/phos_adc/ds_1/"

    data_file_count = 120000

    train_cnt = 80000
    test_cnt = 20000
    val_cnt = 0

    points = 33
    super_res = 8

    perm = list(range(data_file_count))
    random.shuffle(perm)

    if os.path.exists(save_dir):
        print("The save directory already exists. Exit.")
        exit(-1)
    
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
