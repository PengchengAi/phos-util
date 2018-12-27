DATASET="/home/plac/dataset/phos_adc"

python data_analysis/prepare_data_from_list.py --raw_dir "${DATASET}/2018-12-05-11-38-33/" \
  --save_dir "${DATASET}/ds_2/" --train_list "${DATASET}/2018-12-05-11-38-33_train_list.txt" \
  --test_list "${DATASET}/2018-12-05-11-38-33_test_list.txt" \
  --down_sample 24 --points 17 --super_res 16

python data_analysis/prepare_data_from_list.py --raw_dir "${DATASET}/2018-12-05-11-38-33/" \
  --save_dir "${DATASET}/ds_3/" --train_list "${DATASET}/2018-12-05-11-38-33_train_list.txt" \
  --test_list "${DATASET}/2018-12-05-11-38-33_test_list.txt" \
  --down_sample 48 --points 9 --super_res 32

python data_analysis/prepare_data_from_list.py --raw_dir "${DATASET}/2018-12-05-11-38-33/" \
  --save_dir "${DATASET}/ds_4/" --train_list "${DATASET}/2018-12-05-11-38-33_train_list.txt" \
  --test_list "${DATASET}/2018-12-05-11-38-33_test_list.txt" \
  --down_sample 6 --points 65 --super_res 4
