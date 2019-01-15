DATASET="/home/plac/dataset/phos_adc"

python data_analysis_emcal/prepare_data_from_list.py --raw_dir "${DATASET}/2019-01-11-11-17-34/" \
  --save_dir "${DATASET}/dsp_11/" --train_list "${DATASET}/2019-01-11-11-17-34_train_list.txt" \
  --test_list "${DATASET}/2019-01-11-11-17-34_test_list.txt" \
  --down_sample 16 --points 3 --super_res 128 --int_kind "quadratic"

python data_analysis_emcal/prepare_data_from_list.py --raw_dir "${DATASET}/2019-01-11-11-17-34/" \
  --save_dir "${DATASET}/dsc_11/" --train_list "${DATASET}/2019-01-11-11-17-34_train_list.txt" \
  --test_list "${DATASET}/2019-01-11-11-17-34_test_list.txt" \
  --down_sample 16 --points 3 --super_res 128 --coarse 1 --int_kind "quadratic"
