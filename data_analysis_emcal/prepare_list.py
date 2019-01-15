import sys
import os
import random
import argparse
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate

parser = argparse.ArgumentParser()
parser.add_argument("--raw_dir", required=True, help="where the raw data is")
parser.add_argument("--save_dir", required=True, help="where to save processed list")
parser.add_argument("--total_cnt", type=int, default=120000, help="total files in the raw dataset")
parser.add_argument("--train_cnt", type=int, default=80000, help="training dataset size")
parser.add_argument("--test_cnt", type=int, default=20000, help="test dataset size")
parser.add_argument("--val_cnt", type=int, default=0, help="validation dataset size")

parser.add_argument("--freq", type=int, default=125, help="ADC sampling frequency (MHz)")
parser.add_argument("--start_int", type=int, default=28, help="the interval between trigger and pulse start")
parser.add_argument("--label_rnd", type=int, default=4, help="rounding number for the label")
parser.add_argument("--down_sample", type=int, default=1, help="down sampling rate")
parser.add_argument("--points", type=int, default=33, help="how many points in a sample")
parser.add_argument("--super_res", type=int, default=8, help="super resolution ratio")

parser.add_argument("--int_kind", default="cubic", help="interpolation kind")

a = parser.parse_args()

sys.argv = [sys.argv[0]] + ["--input_dir", str(a.raw_dir), "--verbose", str(0)]
print(sys.argv)

import trigger_fit_square

def read_bin_file(data_file):
    arr = np.fromfile(data_file, dtype=np.int32)
    arr = np.reshape(arr, [4, -1])
    pul = arr[0, :]
    tri = arr[1, :]

    return (pul, tri)

def gen_one_sample(data_file, handler):
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
    start_int = a.start_int
    label_rnd = a.label_rnd
    down_sample = a.down_sample
    points = a.points

    ret = trigger_fit_square.tri_process(tri, os.path.basename(data_file), coarse=True)
    if ret is None:
        return -1
    _, refer, _, _ = ret

    x_trigger = refer
    x_start = x_trigger + start_int

    actual_start = int(round(x_start / float(label_rnd))) * label_rnd
    actural_end = actual_start + (points - 1) * down_sample
    if actural_end >= len(pul):
        print("the end point is out of range")
        return -1

    # save
    filename = os.path.split(data_file)[-1]
    handler.write("%s\n" % (filename))
    return 0

def generate_data(start_index, perm, raw_dir, list_path, count):
    raw_data_length = len(perm)

    index = start_index
    count_gen = 0
    print("begin from index:", index)
    with open(list_path, mode="w") as f:
        while count_gen < count:
            if index >= raw_data_length:
                print("finish using raw dataset")
                break
            data_file = os.path.join(raw_dir, "%08d.bin" % (perm[index]+1))
            ret = gen_one_sample(data_file, f)
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

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print("The save directory has been created.")
    
    dir_name = os.path.basename(os.path.normpath(raw_dir))
    train_name = "%s_train_list.txt" % (dir_name)
    test_name = "%s_test_list.txt" % (dir_name)
    val_name = "%s_val_list.txt" % (dir_name)

    train_path = os.path.join(save_dir, train_name)
    test_path = os.path.join(save_dir, test_name)
    val_path = os.path.join(save_dir, val_name)

    if os.path.exists(train_path) or os.path.exists(test_path) or os.path.exists(val_path):
        print("Destination file already exists. Exit.")
        exit(-1)

    # generate data
    start_index = 0
    if train_cnt > 0:
        start_index = generate_data(start_index, perm, raw_dir, train_path, train_cnt)
        print("write %d samples to the training set" % (train_cnt))
    if test_cnt > 0:
        start_index = generate_data(start_index, perm, raw_dir, test_path, test_cnt)
        print("write %d samples to the test set" % (test_cnt))
    if val_cnt > 0:
        _ = generate_data(start_index, perm, raw_dir, val_path, val_cnt)
        print("write %d samples to the validation set" % (val_cnt))

    print("data generation finished")
