import subprocess
import re
import statistics
import numpy as np

COMMAND = "make invoke-action"
RUNS = 50
RESULT_FILE = "result.txt"


def network_delay():
    import requests
    import time
    start = 1000 * time.time()
    for ticker in ['GOOG', 'AMZN', 'MSFT']:
        requests.get(
            url="https://query1.finance.yahoo.com/v8/finance/chart/{}?range=1&interval=1d&includePrePost=False&events=div%2Csplits".
            format(ticker),
            proxies={"https": "http://222.20.68.145:7890"},
            headers={
                'User-Agent': 'Mozilla/5.0'
            }
        )
    end = 1000 * time.time()
    return end - start


# 执行命令并获取输出结果
def run_command(command):
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    return result.stdout


# 从输出结果中提取 interactionTime 和 executeTime 的值
def extract_times(output):
    interaction_time = float(re.search(r'"interactionTime": "([\d.]+) ms"', output).group(1))
    execute_time = float(re.search(r'"executeTime": "([\d.]+) ms"', output).group(1)) + network_delay()
    return interaction_time, execute_time


# 计算中位数和 99 尾延迟
def calculate_stats(times):
    median = statistics.median(times)
    percentile_99 = np.percentile(times, 99)
    return median, percentile_99


# 主程序
def main():
    interaction_times = []
    execute_times = []

    # 执行第一次（冷启动）
    print("Running cold start...")
    cold_start_output = run_command(COMMAND)
    cold_start_interaction_time, cold_start_execute_time = extract_times(cold_start_output)
    print(f"Cold start interaction time: {cold_start_interaction_time} ms")
    print(f"Cold start execute time: {cold_start_execute_time} ms")

    # 重复执行命令
    for i in range(RUNS):
        print(f"Run {i + 1}/{RUNS}...")
        output = run_command(COMMAND)
        interaction_time, execute_time = extract_times(output)
        interaction_times.append(interaction_time)
        execute_times.append(execute_time)

    # 计算中位数和 99 尾延迟
    interaction_median, interaction_percentile_99 = calculate_stats(interaction_times)
    execute_median, execute_percentile_99 = calculate_stats(execute_times)

    # 输出结果
    print("\nResults:")
    print(f"Interaction time median: {interaction_median} ms")
    print(f"Interaction time 99 percentile: {interaction_percentile_99} ms")
    print(f"Execute time median: {execute_median} ms")
    print(f"Execute time 99 percentile: {execute_percentile_99} ms")

    # 将结果写入文件
    with open(RESULT_FILE, "w") as f:
        f.write(f"Cold start interaction time: {cold_start_interaction_time} ms\n")
        f.write(f"Cold start execute time: {cold_start_execute_time} ms\n")
        f.write(f"Interaction time median: {interaction_median} ms\n")
        f.write(f"Interaction time 99 percentile: {interaction_percentile_99} ms\n")
        f.write(f"Execute time median: {execute_median} ms\n")
        f.write(f"Execute time 99 percentile: {execute_percentile_99} ms\n")
    print(f"\nResults saved to {RESULT_FILE}")


if __name__ == "__main__":
    main()
