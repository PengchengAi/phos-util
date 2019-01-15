DATASET="/home/plac/dataset/phos_adc"

python data_analysis_emcal/prepare_data_from_list.py --raw_dir "${DATASET}/2019-01-11-11-17-34/" \
  --save_dir "${DATASET}/dsp_10/" --train_list "${DATASET}/2019-01-11-11-17-34_train_list.txt" \
  --test_list "${DATASET}/2019-01-11-11-17-34_test_list.txt" \
  --down_sample 8 --points 5 --super_res 64

python data_analysis_emcal/prepare_data_from_list.py --raw_dir "${DATASET}/2019-01-11-11-17-34/" \
  --save_dir "${DATASET}/dsc_10/" --train_list "${DATASET}/2019-01-11-11-17-34_train_list.txt" \
  --test_list "${DATASET}/2019-01-11-11-17-34_test_list.txt" \
  --down_sample 8 --points 5 --super_res 64 --coarse 1
