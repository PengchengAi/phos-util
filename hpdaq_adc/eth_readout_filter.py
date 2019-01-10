import time
import json
import multiprocessing
import argparse
import ds_filter
import ethernet

parser = argparse.ArgumentParser()

parser.add_argument("--save_dir", type=str, required=True, help="where to save the ADC data")

parser.add_argument("--tri_type", type=str, default="soft", choices=["soft", "hard"], help="software trigger or hardware trigger")
parser.add_argument("--tri_int", type=float, default=0.1, help="trigger interval for software trigger")
parser.add_argument("--tri_num", type=int, default=100, help="trigger counts for software trigger")
parser.add_argument("--tri_dep", type=int, default=2048, help="trigger depth")
parser.add_argument("--tri_height", type=int, default=50000, help="the height of the trigger signal")
parser.add_argument("--timeout", type=float, default=10.0, help="trigger timeout")

parser.add_argument("--server_addr", type=str, default="192.168.2.3", help="TCP server ip address")
parser.add_argument("--server_port", type=int, default=1024, help="TCP server port")

parser.add_argument("--dis_int", type=int, default=0, help="how often the ADC data is displayed (0 to disable)")
parser.add_argument("--conf_file", type=str, help="input configuration json file")
parser.add_argument("--verbose", type=int, default=1, help="print more information")

a = parser.parse_args()

if __name__ == "__main__":
    # load configuration from json file
    options = vars(a).keys()
    if a.conf_file is not None:
        with open(a.conf_file) as f:
            for key, val in json.loads(f.read()).items():
                if key in options:
                    print("loaded", key, "=", val)
                    setattr(a, key, val)

    if a.tri_type == "soft":
        soft_trigger = True
    else:
        soft_trigger = False
    
    # initialize instances and queues
    eth_inst = ethernet.Eth_hpdaq_adc(server_addr=a.server_addr, server_port=a.server_port, trigger_depth=a.tri_dep,
                                      soft_trigger=soft_trigger, timeout=a.timeout, verbose=a.verbose)
    ds_inst = ds_filter.DS_hpdaq_adc_filter(savedir=a.save_dir, conf=vars(a), max_sample=a.tri_num, dis_interval=a.dis_int,
                                            data_length=a.tri_dep, tri_height=a.tri_height)

    data_queue = multiprocessing.Queue()
    if soft_trigger:
        trigger_queue = multiprocessing.Queue()
    else:
        trigger_queue = None
    
    # start processes
    eth_proc = multiprocessing.Process(target=eth_inst.run, args=(data_queue, trigger_queue,))
    ds_proc = multiprocessing.Process(target=ds_inst.run, args=(data_queue,))

    eth_proc.start()
    ds_proc.start()

    # main routine
    try:
        if soft_trigger:
            for ii in range(a.tri_num):
                if not ds_proc.is_alive() or not eth_proc.is_alive():
                    print("the process exits before soft trigger completes")
                    break
                trigger_queue.put([])
                time.sleep(a.tri_int)

            ds_inst.stop()
            ds_proc.join()

            print("soft trigger exits")
        else:
            while ds_proc.is_alive():
                time.sleep(1)

        # processes exit
        eth_inst.stop()
        eth_proc.join()

        print("the program exits normally")
        exit(0)
    except KeyboardInterrupt:
        # processes exit
        eth_inst.stop()
        ds_inst.stop()

        eth_proc.join()
        ds_proc.join()

        print("the program is aborted")
        exit(-1)
