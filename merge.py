import subprocess

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

# 生成待检测链接列表
with open("urls.txt", "w", encoding="utf-8") as f:
    for fname in m3u_files:
        f.write(CDN_PREFIX + fname + "\n")

# 执行测速合并
subprocess.run([
    "iptv-checker",
    "-i", "urls.txt",
    "-o", "auto_total.m3u",
    "--timeout", "5"
])