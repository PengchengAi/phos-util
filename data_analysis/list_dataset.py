import os

data_dir = "/home/plac/dataset/phos_adc"

train_dir = os.path.join(data_dir, "ds_1", "short", "train")
test_dir = os.path.join(data_dir, "ds_1", "short", "test")

train_txt = os.path.join(data_dir, "2018-12-05-11-38-33_train_list.txt")
test_txt = os.path.join(data_dir, "2018-12-05-11-38-33_test_list.txt")

def get_name(p):
    return os.path.splitext(os.path.basename(p))[0]

train_files = os.listdir(train_dir)
train_files = sorted(train_files, key=lambda path: int(get_name(path)))
with open(train_txt, mode="w") as f:
    for elem in train_files:
        f.write("%s\n" % (elem))

print("finish writing training list")

test_files = os.listdir(test_dir)
test_files = sorted(test_files, key=lambda path: int(get_name(path)))
with open(test_txt, mode="w") as f:
    for elem in test_files:
        f.write("%s\n" % (elem))

print("finish writing test list")
