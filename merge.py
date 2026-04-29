import requests
import sys

# 源仓库CDN地址
BASE_URL = "https://gcore.jsdelivr.net/gh/Wang963963/IPTV-4K-M3U@main/m3u/"

# 所有线路列表
files = [
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

# 合并所有M3U内容
all_lines = ["#EXTM3U"]
for fname in files:
    url = BASE_URL + fname
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        for line in resp.text.splitlines():
            if line.strip() and not line.startswith("#EXTM3U"):
                all_lines.append(line)
        print(f"✅ 已加载: {fname}")
    except Exception as e:
        print(f"❌ 加载失败: {fname} - {e}", file=sys.stderr)

# 写入最终文件
with open("auto_iptv_wang.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(all_lines))

print("\n🎉 聚合完成，文件已生成：auto_iptv_wang.m3u")