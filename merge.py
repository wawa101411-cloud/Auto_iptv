import requests
import os

# 你的源仓库 CDN 加速前缀
CDN_PREFIX = "https://gcore.jsdelivr.net/gh/Wang963963/IPTV-4K-M3U@main/m3u/"

# 你目录下的所有线路（已按你截图整理）
m3u_files = [
    "上海电信.m3u",
    "内蒙古联通.m3u",
    "北京联通.m3u",
    "北京联通1.m3u",
    "北京联通2.m3u",
    "北京联通3.m3u",
    "四川电信.m3u",
    "四川电信1.m3u",
    "安徽电信.m3u",
    "安徽电信1.m3u",
    "安徽电信2.m3u",
    "山西联通.m3u",
    "山西联通1.m3u",
    "广东电信.m3u",
    "广东电信1.m3u",
    "广东电信2.m3u",
    "广东电信3.m3u",
    "江苏电信.m3u",
    "江苏电信1.m3u",
    "河北联通.m3u",
    "河北联通1.m3u",
    "河南联通.m3u",
    "河南联通1.m3u",
    "浙江电信.m3u",
    "浙江电信1.m3u",
    "浙江电信2.m3u",
    "浙江电信3.m3u",
    "浙江电信4.m3u",
    "湖北电信.m3u",
    "湖南电信.m3u",
    "贵州电信.m3u",
    "辽宁联通.m3u",
    "重庆联通.m3u",
    "重庆联通1.m3u",
    "重庆联通2.m3u",
    "重庆联通3.m3u",
    "陕西电信.m3u",
    "陕西电信1.m3u",
    "黑龙江联通.m3u"
]

# 1. 下载所有子m3u内容并合并
merged_lines = ["#EXTM3U"]
for fname in m3u_files:
    url = CDN_PREFIX + fname
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        lines = resp.text.splitlines()
        # 跳过子m3u里的#EXTM3U，只保留频道
        for line in lines:
            if line.strip() and not line.startswith("#EXTM3U"):
                merged_lines.append(line)
    except Exception as e:
        print(f"下载失败: {fname} - {e}")

# 2. 写入最终聚合文件
with open("auto_iptv_wang.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(merged_lines))

print("✅ 聚合完成，已生成 auto_iptv_wang.m3u")