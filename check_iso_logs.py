import os
import re

def analyze_iso_log(log_file_path):
    """
    分析单个日志文件，判断是否存在问题
    返回：(是否有问题, 问题描述, 相关信息)
    """
    try:
        with open(log_file_path, "r", encoding="utf-8", errors="ignore") as f:
            log_content = f.read()
        
        # 初始化问题列表
        issues = []
        details = {}
        
        # 1. 检查是否有打包失败（CalledProcessError）
        if "CalledProcessError" in log_content or "返回码：" in log_content and "错误详情：" in log_content:
            issues.append("Pack command failed")
        
        # 2. 检查 ISO 大小校验失败（<1GB）
        if "ISO 大小仅" in log_content and "未达到1GB阈值" in log_content:
            size_match = re.search(r"ISO 大小仅 ([0-9.]+)GB", log_content)
            if size_match:
                issues.append(f"ISO size abnormal ({size_match.group(1)}GB < 1GB)")
                details["Abnormal size"] = f"{size_match.group(1)}GB"
        
        # 3. 检查重复打包（存在两次及以上 extents written）
        extent_matches = re.findall(r"(\d+) extents written \((\d+) MB\)", log_content)
        if len(extent_matches) >= 2:
            issues.append("Duplicate packaging")
            details["Pack records"] = []
            for i, (extents, size_mb) in enumerate(extent_matches, 1):
                size_gb = round(int(size_mb) / 1024, 2)
                details["Pack records"].append(f"Times {i}: {size_gb}GB")
        
        # 4. 检查有效视频文件缺失（无有效 .m2ts）
        if "无有效 .m2ts 视频文件" in log_content:
            issues.append("BDMV missing valid video files")
        
        # 5. 检查 STREAM 目录缺失
        if "缺少 STREAM 目录" in log_content:
            issues.append("BDMV missing STREAM directory")
        
        # 判断是否有问题
        if issues:
            return (True, " | ".join(issues), details)
        else:
            # 无明显问题，但检查是否有正常打包记录（确认日志有效）
            if len(extent_matches) == 1:
                size_gb = round(int(extent_matches[0][1]) / 1024, 2)
                details["Normal size"] = f"{size_gb}GB"
            return (False, "No abnormalities", details)
    
    except Exception as e:
        return (True, f"Log file read failed: {str(e)}", {})

def batch_check_logs(root_log_dir):
    """
    批量检查日志目录下所有日志文件
    """
    # 结果汇总
    result_summary = {
        "Total logs": 0,
        "Problem logs": 0,
        "Problem details": []
    }
    
    # 遍历所有日志文件（递归遍历子目录）
    for root, dirs, files in os.walk(root_log_dir):
        for file in files:
            if file.endswith(".log"):  # 仅检查 .log 文件
                log_file = os.path.join(root, file)
                result_summary["Total logs"] += 1
                
                # 分析单个日志
                has_issue, issue_desc, details = analyze_iso_log(log_file)
                
                if has_issue:
                    result_summary["Problem logs"] += 1
                    result_summary["Problem details"].append({
                        "Log path": log_file,
                        "Issue description": issue_desc,
                        "Related info": details
                    })
    
    # 输出汇总结果
    print("=" * 80)
    print("ISO Log Batch Check Result Summary")
    print("=" * 80)
    print(f"Total checked logs: {result_summary['Total logs']}")
    print(f"Problem logs: {result_summary['Problem logs']}")
    print(f"Normal logs: {result_summary['Total logs'] - result_summary['Problem logs']}")
    print()
    
    # 输出有问题的日志详情
    if result_summary["Problem details"]:
        print("Problem Log Details:")
        print("-" * 80)
        for i, detail in enumerate(result_summary["Problem details"], 1):
            print(f"\n{i}. Log path: {detail['Log path']}")
            print(f"   Issue description: {detail['Issue description']}")
            if detail["Related info"]:
                print("   Related info:")
                for key, value in detail["Related info"].items():
                    if isinstance(value, list):
                        for item in value:
                            print(f"     - {item}")
                    else:
                        print(f"     - {key}: {value}")
        print("-" * 80)
    else:
        print("All logs are normal!")

if __name__ == "__main__":
    # 日志根目录（默认是 /home/boxbox/logs）
    LOG_ROOT_DIR = "/home/boxbox/logs_bdmv/bdmv_packaging/"
    
    # 检查目录是否存在
    if not os.path.exists(LOG_ROOT_DIR):
        print(f"Error: Directory {LOG_ROOT_DIR} does not exist, please check the path")
        exit(1)
    
    # 开始批量检查
    print(f"Start checking log directory: {LOG_ROOT_DIR}")
    batch_check_logs(LOG_ROOT_DIR)
