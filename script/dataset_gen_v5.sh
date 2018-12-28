DATASET="/home/plac/dataset/phos_adc"

python data_analysis/prepare_data_from_list.py --raw_dir "${DATASET}/2018-12-05-11-38-33/" \
  --save_dir "${DATASET}/ds_5/" --train_list "${DATASET}/2018-12-05-11-38-33_train_list.txt" \
  --test_list "${DATASET}/2018-12-05-11-38-33_test_list.txt" \
  --down_sample 96 --points 5 --super_res 64
