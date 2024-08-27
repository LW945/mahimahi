import argparse
import re
import math
import os
import numpy as np
import random

def select_trace(cfg):
    trace_input_file = cfg.input_file
    loss_num_threshold = 1000
    cnt = 0

    for files in os.listdir(trace_input_file):
        if ("eth" in files) or ("cell" in files) or ("wifi" in files):
            loss_rate_cnt = 0
            with open(trace_input_file + "/" + files, "r") as f:
                for line in f.readlines():
                    line = line.split(" ")
                    lossrate_tmp = re.sub(r'[a-zA-Z]', '', line[2])
                    if float(lossrate_tmp) > 0:
                        loss_rate_cnt += 1
                    if loss_rate_cnt > loss_num_threshold:
                        print(files)
                        cnt += 1
                        break

# the format is bandwidth, rtt, lossrate
def prepare_trace_from_hairpin(cfg):
    trace_input_file = cfg.input_file
    trace_output_dir = cfg.output_dir

    input_file_name = trace_input_file.split("/")[-1]

    bandwith, lossrate = [], []
    source_trace_len = 0
    target_trace_len = 600
    split_num = 0

    with open(trace_input_file, "r") as f:
        for line in f.readlines():
            line = line.split(" ")
            bandwith_ = re.sub(r'[a-zA-Z]', '', line[0])
            lossrate_ = re.sub(r'[a-zA-Z]', '', line[2])

            if float(lossrate_) < 0:
                continue

            bandwith.append(float(bandwith_))
            lossrate.append(float(lossrate_))
    source_trace_len = len(bandwith)

    for i in range(0, source_trace_len, target_trace_len):
        if i + target_trace_len > source_trace_len:
            break

        bandwith_tmp = np.array(bandwith[i:i+target_trace_len])
        lossrate_tmp = np.array(lossrate[i:i+target_trace_len])

        avg_bandwith = np.mean(bandwith_tmp)
        ajusted_bandwith = bandwith_tmp * 30 / avg_bandwith

        loss_rate_cnt = 0

        for elem in lossrate_tmp:
            if elem > 0.0:
                loss_rate_cnt += 1

        if loss_rate_cnt < 10:
            continue
        else:
            idx = 0
            while loss_rate_cnt > 10:
                rand_num = random.randint(0, 1)
                if rand_num == 0 and lossrate_tmp[idx] > 0.0:
                    lossrate_tmp[idx] = 0.0
                    bandwith_tmp[idx] = 30.0
                    loss_rate_cnt -= 1
                idx += 1
                idx %= target_trace_len

        bandwith_trace_file_down_link = trace_output_dir + "/bandwidth_trace_down_link_" + str(split_num) + "_" + input_file_name
        bandwith_trace_file_up_link = trace_output_dir + "/bandwidth_trace_up_link_" + str(split_num) + "_" + input_file_name
        lossrate_trace_file = trace_output_dir + "/lossrate_trace_" + str(split_num) + "_" + input_file_name

        time_stamp = 0

        f1 = open(bandwith_trace_file_down_link, "w")
        f2 = open(bandwith_trace_file_up_link, "w")

        for elem in ajusted_bandwith:
            transmit_bytes = (elem * 1000 * 30) / 8
            total_pkts = math.ceil(transmit_bytes / 1500)
            per_ms_pkts = total_pkts // 30
            time_list = [per_ms_pkts for _ in range(30)]
            total_pkts -= per_ms_pkts * 30
            while total_pkts > 0:
                per_pkt_ms = 30 // total_pkts
                for i in range(0, 30, per_pkt_ms):
                    if total_pkts == 0:
                        break
                    time_list[i] += 1
                    total_pkts -= 1

            for i in range(30):
                for _ in range(time_list[i]):
                    f1.write(str(time_stamp+i+1) + "\n")
                    f2.write(str(time_stamp+i+1) + "\n")

            time_stamp += 30

        f1.close()
        f2.close()

        with open(lossrate_trace_file, "w") as f:
            time_stamp = 30
            for l in lossrate_tmp:
                f.write(str(time_stamp) + "," + str(l) + "\n")
                time_stamp += 30
        f.close()

        split_num += 1

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--operation", type=str, default="prepare_trace")
    parser.add_argument("--format", type=str, default="hairpin")
    parser.add_argument("--input_file", type=str, default="")
    parser.add_argument("--output_dir", type=str, default="./") 
    return parser.parse_args()

if __name__ == "__main__":
    cfg = parse_args()
    if cfg.operation == "prepare_trace":
        if cfg.format == "hairpin":
            prepare_trace_from_hairpin(cfg)
    elif cfg.operation == "select_trace":
        select_trace(cfg)
    else:
        print("Not supported format")