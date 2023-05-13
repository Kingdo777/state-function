import subprocess
import re
import statistics
import time

import numpy as np

RUNS = 1
RESULT_FILE = "result.txt"


# 执行命令并获取输出结果
def run_command(command):
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    return result.stdout


# 从输出结果中提取 interactionTime 和 executeTime 的值
def extract_times(output):
    execute_time = float(re.search(r'"executeTime": ([\d.]+)', output).group(1))
    init_time = float(re.search(r'"initTime": ([\d.]+)', output).group(1))
    interaction_time = float(re.search(r'"interactionTime": ([\d.]+)', output).group(1))
    request_time = float(re.search(r'"requestTime": ([\d.]+)', output).group(1))
    serialize_time = float(re.search(r'"serializeTime": ([\d.]+)', output).group(1))

    return execute_time, init_time, interaction_time, request_time, serialize_time


# 计算中位数和 99 尾延迟
def calculate_stats(times):
    print(times)
    median = statistics.median(times)
    percentile_99 = np.percentile(times, 99)
    min_time = min(times)
    return median, percentile_99, min_time


def main(op):
    execute_times = []
    init_times = []
    interaction_times = []
    request_times = []
    serialize_times = []

    cmd = "make action_invoke_{}".format(op)

    # 执行第一次（冷启动）
    print("Running cold start...")
    cold_start_output = run_command(cmd)
    cold_start_execute_time, cold_start_init_time, cold_start_interaction_time, cold_start_request_time, cold_start_serialize_time = \
        extract_times(cold_start_output)
    # print(f"Cold start interaction time: {cold_start_interaction_time} ms")
    # print(f"Cold start execute time: {cold_start_execute_time} ms")
    # print(f"Cold start serialize time: {cold_start_serialize_time} ms")
    # print(f"Cold start init time: {cold_start_init_time} ms")
    # print(f"Cold start request time: {cold_start_request_time} ms")

    # 将冷启动时间添加到相应的列表中
    # execute_times.append(cold_start_execute_time)
    # init_times.append(cold_start_init_time)
    # interaction_times.append(cold_start_interaction_time)
    # request_times.append(cold_start_request_time)
    # serialize_times.append(cold_start_serialize_time)

    # 重复执行命令
    for i in range(RUNS):
        print(f"Run {i + 1}/{RUNS}...")
        for i in range(3):
            try:
                output = run_command(cmd)
                execute_time, init_time, interaction_time, request_time, serialize_time = extract_times(output)
                execute_times.append(execute_time)
                init_times.append(init_time)
                interaction_times.append(interaction_time)
                request_times.append(request_time)
                serialize_times.append(serialize_time)
                break
            except Exception:
                print(f"Run {i + 1}/{RUNS} failed, retrying {i + 1}/{3}")
                continue

        time.sleep(1)

    # 计算中位数、99尾延迟和最小值
    interaction_median, interaction_percentile_99, interaction_min_time = calculate_stats(interaction_times)
    execute_median, execute_percentile_99, execute_min_time = calculate_stats(execute_times)
    serialize_median, serialize_percentile_99, serialize_min_time = calculate_stats(serialize_times)
    init_median, init_percentile_99, init_min_time = calculate_stats(init_times)
    request_median, request_percentile_99, request_min_time = calculate_stats(request_times)

    # 输出结果
    print("\nResults:")
    print(f"\t\t\t median\t 99ile\t min\t")
    print(f"Interaction: {interaction_median:.1f}\t {interaction_percentile_99:.1f}\t {interaction_min_time:.1f}\t")
    print(f"Execute:\t {execute_median:.1f}\t {execute_percentile_99:.1f}\t {execute_min_time:.1f}\t")
    print(f"Serialize:\t {serialize_median:.1f}\t {serialize_percentile_99:.1f}\t {serialize_min_time:.1f}\t")
    print(f"Init:\t\t {init_median:.1f}\t {init_percentile_99:.1f}\t {init_min_time:.1f}\t")
    print(f"Request:\t {request_median:.1f}\t {request_percentile_99:.1f}\t {request_min_time:.1f}\t\n")

    # 将结果写入文件
    with open("result-{}.txt".format(op), "w") as f:
        f.write(f"Cold start interaction time: {cold_start_interaction_time} ms\n")
        f.write(f"Cold start execute time: {cold_start_execute_time} ms\n")
        f.write(f"Cold start serialize time: {cold_start_serialize_time} ms\n")
        f.write(f"Cold start init time: {cold_start_init_time} ms\n")
        f.write(f"Cold start request time: {cold_start_request_time} ms\n")
        f.write("\n\n")
        f.write(f"\t\t\t median\t 99ile\t min\t\n")
        f.write(
            f"Interaction: {interaction_median:.1f}\t {interaction_percentile_99:.1f}\t {interaction_min_time:.1f}\t\n")
        f.write(f"Execute:\t {execute_median:.1f}\t {execute_percentile_99:.1f}\t {execute_min_time:.1f}\t\n")
        f.write(f"Serialize:\t {serialize_median:.1f}\t {serialize_percentile_99:.1f}\t {serialize_min_time:.1f}\t\n")
        f.write(f"Init:\t\t {init_median:.1f}\t {init_percentile_99:.1f}\t {init_min_time:.1f}\t\n")
        f.write(f"Request:\t {request_median:.1f}\t {request_percentile_99:.1f}\t {request_min_time:.1f}\t\n")


if __name__ == "__main__":
    # run_command("make clean")
    main("Openwhisk")
    print("############################################")
    # run_command("make clean")
    main("OFC")
    print("############################################")
    # run_command("make clean")
    main("Faastorage")
    print("############################################")
    # run_command("make clean")
    main("Faastlane")
