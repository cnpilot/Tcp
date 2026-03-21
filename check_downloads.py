import os
from pathlib import Path

def get_folder_size(folder_path):
    """
    计算文件夹的总大小（递归），返回字节数
    
    Args:
        folder_path (str): 文件夹路径
    
    Returns:
        int: 文件夹总大小（字节）
    """
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                # 跳过符号链接，避免循环和权限问题
                if not os.path.islink(fp):
                    try:
                        total_size += os.path.getsize(fp)
                    except OSError:
                        # 忽略无法访问的文件
                        continue
    except PermissionError:
        print(f"警告：无法访问 {folder_path}，跳过大小计算")
    return total_size

def format_size(bytes_size):
    """
    将字节数格式化为易读的单位（B/KB/MB/GB/TB）
    
    Args:
        bytes_size (int): 字节数
    
    Returns:
        str: 格式化后的大小字符串
    """
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    size = bytes_size
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.2f} {units[unit_index]}"

def check_directory_structure(target_dir):
    """
    检查指定目录的结构，统计相关信息
    
    Args:
        target_dir (str): 要检查的目标目录路径
    
    Returns:
        dict: 包含所有统计结果的字典
    """
    # 初始化统计变量（新增iso_count相关字段）
    stats = {
        "total_subfolders": 0,          # 一级子文件夹总数
        "has_bdmv": 0,                  # 包含BDMV文件夹的子文件夹数
        "has_iso": 0,                   # 包含ISO文件的子文件夹数
        "no_iso": 0,                    # 不包含ISO文件的子文件夹数
        "has_both_bdmv_iso": 0,         # 同时包含BDMV和ISO的子文件夹数
        "folders_with_bdmv": [],        # 包含BDMV的文件夹列表
        "folders_with_iso": [],         # 包含ISO的文件夹列表（元组：(路径, ISO数量, 大小)）
        "folders_without_iso": [],      # 不包含ISO文件的文件夹列表
        "folders_with_both": []         # 同时包含BDMV和ISO的文件夹列表（元组：(路径, ISO数量, 大小)）
    }
    
    # 验证目标目录是否存在
    if not os.path.exists(target_dir):
        print(f"错误：目录 {target_dir} 不存在！")
        return None
    
    # 获取一级子文件夹列表
    try:
        subfolders = [f for f in os.listdir(target_dir) 
                     if os.path.isdir(os.path.join(target_dir, f))]
        stats["total_subfolders"] = len(subfolders)
        
        # 遍历每个一级子文件夹
        for folder in subfolders:
            folder_path = os.path.join(target_dir, folder)
            
            # 检查是否包含BDMV文件夹（递归查找）
            bdmv_found = False
            for root, dirs, files in os.walk(folder_path):
                if "BDMV" in dirs:
                    bdmv_found = True
                    stats["folders_with_bdmv"].append(folder_path)
                    break
            
            if bdmv_found:
                stats["has_bdmv"] += 1
            
            # 检查是否包含ISO文件（递归查找），并统计数量
            iso_found = False
            iso_count = 0  # 新增：统计ISO文件数量
            folder_size = 0  # 初始化文件夹大小
            
            # 遍历所有文件统计ISO数量
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if file.lower().endswith('.iso'):
                        iso_found = True
                        iso_count += 1  # 累计ISO数量
            
            # 如果找到ISO文件，计算文件夹大小
            if iso_found:
                folder_size = get_folder_size(folder_path)
                # 存储路径、ISO数量、大小
                stats["folders_with_iso"].append((folder_path, iso_count, folder_size))
                stats["has_iso"] += 1
            else:
                stats["no_iso"] += 1
                stats["folders_without_iso"].append(folder_path)
            
            # 新增：检查是否同时包含BDMV和ISO
            if bdmv_found and iso_found:
                stats["has_both_bdmv_iso"] += 1
                stats["folders_with_both"].append((folder_path, iso_count, folder_size))
                
    except PermissionError:
        print(f"错误：没有权限访问目录 {target_dir}")
        return None
    except Exception as e:
        print(f"发生错误：{str(e)}")
        return None
    
    # 对包含ISO的文件夹按大小排序（由小到大）
    stats["folders_with_iso"].sort(key=lambda x: x[2])
    # 对同时包含BDMV和ISO的文件夹按大小排序
    stats["folders_with_both"].sort(key=lambda x: x[2])
    
    return stats

def display_results(stats, target_dir):
    """
    格式化显示统计结果（新增ISO数量显示）
    """
    if not stats:
        return
    
    print("=" * 80)
    print("目录结构检查结果")
    print("=" * 80)
    print(f"目标目录: {target_dir}")
    print(f"\n1. 一级子文件夹总数: {stats['total_subfolders']}")
    print(f"2. 包含BDMV文件夹的子文件夹数: {stats['has_bdmv']}")
    print(f"3. 包含ISO文件的子文件夹数: {stats['has_iso']}")
    print(f"4. 不包含ISO文件的子文件夹数: {stats['no_iso']}")
    print(f"5. 同时包含BDMV文件夹和ISO文件的子文件夹数: {stats['has_both_bdmv_iso']}")
    
    # 显示详细列表（可选）
    print("\n" + "-" * 80)
    print("详细信息:")
    print("-" * 80)
    
    if stats["folders_with_bdmv"]:
        print("\n包含BDMV文件夹的目录:")
        for folder in stats["folders_with_bdmv"]:
            print(f"  - {folder}")
    else:
        print("\n没有找到包含BDMV文件夹的目录")
    
    if stats["folders_with_iso"]:
        print("\n包含ISO文件的目录（按大小由小到大排序）:")
        for idx, (folder, iso_count, size) in enumerate(stats["folders_with_iso"], 1):
            formatted_size = format_size(size)
            # 显示ISO数量和总大小
            print(f"  {idx}. {folder} (含 {iso_count} 个ISO文件, 总大小: {formatted_size})")
    else:
        print("\n没有找到包含ISO文件的目录")
    
    # 显示同时包含BDMV和ISO的目录
    if stats["folders_with_both"]:
        print("\n同时包含BDMV文件夹和ISO文件的目录（按大小由小到大排序）:")
        for idx, (folder, iso_count, size) in enumerate(stats["folders_with_both"], 1):
            formatted_size = format_size(size)
            print(f"  {idx}. {folder} (含 {iso_count} 个ISO文件, 总大小: {formatted_size})")
    else:
        print("\n没有找到同时包含BDMV文件夹和ISO文件的目录")
    
    if stats["folders_without_iso"]:
        print("\n不包含ISO文件的目录:")
        for folder in stats["folders_without_iso"]:
            print(f"  - {folder}")
    else:
        print("\n所有目录都包含ISO文件")
    
    print("\n" + "=" * 80)

# 主程序
if __name__ == "__main__":
    # 目标目录
    target_directory = "/home/boxbox/qbittorrent/download"
    
    # 执行检查
    results = check_directory_structure(target_directory)
    
    # 显示结果
    if results:
        display_results(results, target_directory)
