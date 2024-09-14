import re
import concurrent.futures
import json
import os
import sys
from tronpy import Tron
from collections import defaultdict

# 定义靓号的模式，匹配连续出现6次及以上的字符
pattern = re.compile(r'(.)\1{5,}')

def generate_wallets(num_wallets):
    tron = Tron()
    wallets = []
    for _ in range(num_wallets):
        account = tron.generate_address()
        wallets.append({"address": account['base58check_address'], "private_key": account['private_key']})
    return wallets

def classify_address(address):
    match = pattern.search(address)
    if match:
        char, length = match.group(1), len(match.group(0))
        pos = address.find(match.group(0))
        if char.isdigit():
            position = "头" if pos == 0 else "尾" if pos + length == len(address) else "中"
            return f"数字连续{length}个_{position}"
        elif char.isalpha():
            position = "头" if pos == 0 else "尾" if pos + length == len(address) else "中"
            return f"英文连续{length}个_{position}"
    return "不符合靓号标准"

def update_display(categories_count):
    sys.stdout.write('\033[H')
    display_lines = [f"\n{category}[{count}]" for category, count in categories_count.items()]
    sys.stdout.write('\n'.join(display_lines) + '\n')
    sys.stdout.flush()

def find_vanity_address(pattern, num_processes, num_wallets_per_process):
    categories = {f"{typ}连续{length}个_{pos}": [] 
                  for typ in ("数字", "英文") 
                  for length in range(6, 10) 
                  for pos in ("头", "中", "尾")}
    categories.update({f"{typ}连续9个以上_{pos}": [] 
                       for typ in ("数字", "英文") 
                       for pos in ("头", "中", "尾")})

    categories_count = defaultdict(int)

    # 加载现有的JSON文件数据
    for category in categories.keys():
        filename = f"{category}.json"
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                categories[category] = data
                categories_count[category] += len(data)

    def process_wallets(wallets):
        for result in wallets:
            address = result['address']
            classification = classify_address(address)
            if classification != "不符合靓号标准":
                categories[classification].append(result)
                categories_count[classification] += 1
                filename = f"{classification}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(categories[classification], f, ensure_ascii=False, indent=4)
        update_display(categories_count)

    with concurrent.futures.ProcessPoolExecutor(max_workers=num_processes) as executor:
        while True:
            futures = [executor.submit(generate_wallets, num_wallets_per_process) for _ in range(num_processes)]
            for future in concurrent.futures.as_completed(futures):
                process_wallets(future.result())

if __name__ == '__main__':
    # 默认进程数和每个进程生成的钱包数量
    num_processes = 11
    num_wallets_per_process = 10000  # 增加每批次生成的钱包数量

    # 无限循环生成并分类地址
    find_vanity_address(pattern, num_processes, num_wallets_per_process)
