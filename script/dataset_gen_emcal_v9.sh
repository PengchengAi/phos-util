DATASET="/home/plac/dataset/phos_adc"

python data_analysis_emcal/prepare_data_from_list.py --raw_dir "${DATASET}/2019-01-11-11-17-34/" \
  --save_dir "${DATASET}/dsp_9/" --train_list "${DATASET}/2019-01-11-11-17-34_train_list.txt" \
  --test_list "${DATASET}/2019-01-11-11-17-34_test_list.txt" \
  --down_sample 4 --points 9 --super_res 32

python data_analysis_emcal/prepare_data_from_list.py --raw_dir "${DATASET}/2019-01-11-11-17-34/" \
  --save_dir "${DATASET}/dsc_9/" --train_list "${DATASET}/2019-01-11-11-17-34_train_list.txt" \
  --test_list "${DATASET}/2019-01-11-11-17-34_test_list.txt" \
  --down_sample 4 --points 9 --super_res 32 --coarse 1
