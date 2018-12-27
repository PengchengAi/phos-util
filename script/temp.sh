DATASET="/home/plac/dataset/phos_adc"

python data_analysis/prepare_data_from_list.py --raw_dir "${DATASET}/2018-12-05-11-38-33/" \
  --save_dir "${DATASET}/ds_test_list/" --train_list "${DATASET}/t_train_list.txt" \
  --test_list "${DATASET}/t_test_list.txt" --down_sample 24 --points 17 --super_res 16
