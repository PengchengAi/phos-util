import os
import argparse
import numpy as np
import lmfit
import matplotlib.pyplot as plt
from scipy.stats import norm

parser = argparse.ArgumentParser()
parser.add_argument("--input_dir", required=True, help="input directory")
parser.add_argument("--file_cnt", type=int, default=1000, help="file count")
parser.add_argument("--verbose", type=int, default=1, help="whether to print and plot the result")

a = parser.parse_args()

def step_response(x, t_0, T1, T2, K, base):
    f = lambda t: K * (1 + T1 / (T2 - T1) * np.exp(-(t - t_0) / T2) - T2 / (T2 - T1) * np.exp(-(t - t_0) / T1))
    res = np.piecewise(x, [x < t_0, x >= t_0], [base, f])
    return res

def trigger(x, t_0, T1, T2, K, base, w):
    f = lambda t: step_response(t, t_0, T1, T2, K, base) - step_response(t, t_0+w, T1, T2, K, base)
    return f(x)

def consecutive(data, stepsize=1):
    return np.split(data, np.where(np.diff(data) != stepsize)[0]+1)

def read_bin_file(data_file):
    arr = np.fromfile(data_file, dtype=np.int32)
    arr = np.reshape(arr, [4, -1])
    pul = arr[0, :]
    tri = arr[1, :]

    return (pul, tri)

def tri_process(tri, title, thresh=200):
    # convert to numpy array
    arr = np.array(tri, dtype=np.int32)
    # reject signal with step
    if np.abs(arr[0] - arr[-1]) >= 100:
        print("there is a step in the trigger signal")
        return None
    # get min and max
    tmin = np.min(arr)
    tmax = np.max(arr)
    # get the most frequent point value
    most_value = np.argmax(np.bincount(arr - tmin))
    most_value = most_value + tmin
    # clip the array to most_points
    arr_clip = np.clip(arr, most_value, None)
    # get the number of valid points
    valid_num = np.sum(np.bincount(arr_clip - most_value)[thresh:])
    # cluster valid points
    valid_points = np.where(arr_clip >= most_value + thresh)[0]
    valid_cluster = consecutive(valid_points)
    valid_cluster_num = list(map(lambda x: x.shape[0], valid_cluster))
    # select the longest cluster
    select_points = valid_cluster[np.argmax(valid_cluster_num)]
    select_points_num = len(select_points)
    # print information
    print("min:", tmin, "max:", tmax, "most:", most_value, "valid num:", valid_num,
          "cluster:", valid_cluster_num, "select:", select_points_num)
    
    # process select points
    refer_point = select_points[0]
    norm_points = (arr_clip[select_points] - most_value) / 25000
    
    # fit model
    T1, T2 = 3.336, 45.047
    w = 2.988
    base = 0
    # tri_simple = lambda x, t_0, T1, T2, K, w: trigger(x, t_0, T1, T2, K, base, w)
    tri_simple = lambda x, t_0, K: trigger(x, t_0, T1, T2, K, base, w)
    xval = np.linspace(0, select_points_num, select_points_num, endpoint=False)
    yval = norm_points
    gmodel = lmfit.Model(tri_simple)
    # result = gmodel.fit(yval, x=xval, t_0=0.0, T1=2.0, T2=4.0, K=3, w=0.3)
    result = gmodel.fit(yval, x=xval, t_0=0.0, K=1.348)

    best_t_0 = result.best_values["t_0"]
    label_t_0 = refer_point + best_t_0
    dev_t_0 = result.params["t_0"].stderr

    # print and plot result
    if a.verbose:
        print(result.fit_report())
        print("reference:", refer_point, "best:", best_t_0, "label:", label_t_0, "std:", dev_t_0)
        plt.title(title)
        plt.plot(xval, yval, 'bo')
        plt.plot(xval, result.init_fit, 'k--')
        plt.plot(xval, result.best_fit, 'r-')
        plt.show()

    return (len(valid_cluster) > 1, refer_point, label_t_0, dev_t_0)

def fit_hist(datos):
    # best fit of data
    (mu, sigma) = norm.fit(datos)

    # the histogram of the data
    _, bins, _ = plt.hist(datos, 60, density=True, facecolor='green', alpha=0.75)

    # add a 'best fit' line
    y = norm.pdf(bins, mu, sigma)
    _ = plt.plot(bins, y, 'r--', linewidth=2)

    #plot
    plt.xlabel('Residual')
    plt.ylabel('Probability')
    plt.title(r'$\mathrm{Histogram\ of\ residual:}\ \mu=%.5f,\ \sigma=%.5f$' %(mu, sigma))
    plt.grid(True)

    plt.show()

if __name__ == "__main__":
    input_dir = a.input_dir
    file_cnt = a.file_cnt

    if not os.path.exists(input_dir):
        print("Input directory does not exist. Exit.")
        exit(-1)

    valid_cnt = 0

    multi_cnt = 0
    refer_list = []
    label_list = []
    stderr_avg = 0.0
    for i in range(file_cnt):
        # process the trigger signal
        fn = "%08d.bin" % (i+1)
        fn = os.path.join(input_dir, fn)
        _, tri = read_bin_file(fn)
        ret = tri_process(tri, os.path.basename(fn))
        # if not valid, continue
        if ret is None:
            continue
        # if valid, do some work afterwards
        valid_cnt += 1
        multi, refer, label, stderr = ret
        if multi:
            multi_cnt += 1
        refer_list.append(refer)
        label_list.append(label)
        stderr_avg += stderr

    # label distribution
    refer_list = np.array(refer_list, dtype=np.float32)
    label_list = np.array(label_list, dtype=np.float32)
    diff_list = label_list - refer_list
    diff_list = np.reshape(diff_list, [-1])
    fit_hist(diff_list)
    
    # average standard error
    stderr_avg = stderr_avg / valid_cnt

    print("there are %d sample(s) with more than one cluster" % (multi_cnt))
    print("average standard error in t_0:", stderr_avg)
    print("Finish")
