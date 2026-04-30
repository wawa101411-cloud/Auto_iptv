import asyncio
import aiohttp
import re
from collections import defaultdict

# ============ 配置区 ============

# 源仓库CDN地址
BASE_URL = "https://gcore.jsdelivr.net/gh/Wang963963/IPTV-4K-M3U@main/m3u/"
BASE_URL_RAW = "https://raw.githubusercontent.com/Wang963963/IPTV-4K-M3U/main/m3u/"

# 所有线路列表（按优先级排序，越靠前优先级越高）
FILES = [
    # 电信源优先
    "上海电信.m3u",
    "广东电信.m3u",
    "广东电信1.m3u",
    "广东电信2.m3u",
    "广东电信3.m3u",
    "四川电信.m3u",
    "四川电信1.m3u",
    "浙江电信.m3u",
    "浙江电信1.m3u",
    "浙江电信2.m3u",
    "浙江电信3.m3u",
    "浙江电信4.m3u",
    "江苏电信.m3u",
    "江苏电信1.m3u",
    "安徽电信.m3u",
    "安徽电信1.m3u",
    "安徽电信2.m3u",
    "湖北电信.m3u",
    "湖南电信.m3u",
    "贵州电信.m3u",
    "陕西电信.m3u",
    "陕西电信1.m3u",
    # 联通源
    "北京联通.m3u",
    "北京联通1.m3u",
    "北京联通2.m3u",
    "北京联通3.m3u",
    "内蒙古联通.m3u",
    "山西联通.m3u",
    "山西联通1.m3u",
    "河北联通.m3u",
    "河北联通1.m3u",
    "河南联通.m3u",
    "河南联通1.m3u",
    "辽宁联通.m3u",
    "重庆联通.m3u",
    "重庆联通1.m3u",
    "重庆联通2.m3u",
    "重庆联通3.m3u",
    "黑龙江联通.m3u",
]

# 输出配置
OUTPUT_FILE = "auto_iptv_wang.m3u"
MAX_SOURCES_PER_CHANNEL = 5

# 你使用的运营商（影响排序优先级）：telecom / unicom
MY_ISP = "telecom"


# ============ 下载与解析 ============

async def download_m3u(session, fname):
    urls = [BASE_URL + fname, BASE_URL_RAW + fname]
    for attempt in range(3):
        for url in urls:
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        if len(text) > 20:
                            print(f"  ✓ {fname} ({len(text)} bytes)")
                            return text
                    print(f"  ✗ {fname} status={resp.status}, 重试{attempt+1}/3")
            except Exception as e:
                print(f"  ✗ {fname} 异常, 重试{attempt+1}/3")
            await asyncio.sleep(1)
    print(f"  ✗✗ {fname} 跳过")
    return None


def parse_m3u(content, source_name=""):
    channels = []
    lines = content.strip().split('\n')
    current_info = None

    for line in lines:
        line = line.strip()
        if not line or line == "#EXTM3U":
            continue
        if line.startswith("#EXTINF"):
            current_info = line
        else:
            if current_info:
                name_match = re.search(r',(.+)$', current_info)
                channel_name = name_match.group(1).strip() if name_match else "未知频道"
                channels.append((channel_name, current_info, line, source_name))
                current_info = None

    return channels


# ============ 智能排序 ============

def get_source_priority(source_name):
    """根据用户运营商给来源排序，匹配的排前面"""
    if MY_ISP == "telecom" and "电信" in source_name:
        return 0
    if MY_ISP == "unicom" and "联通" in source_name:
        return 0
    if "电信" in source_name:
        return 1
    if "联通" in source_name:
        return 2
    return 3


def build_optimized_m3u(all_channels):
    """按频道分组，同频道多源按运营商优先级排序"""
    channel_groups = defaultdict(list)

    for channel_name, info_line, url, source_name in all_channels:
        priority = get_source_priority(source_name)
        exists = any(u == url for _, _, u, _ in channel_groups[channel_name])
        if not exists:
            channel_groups[channel_name].append((priority, info_line, url, source_name))

    output_lines = ["#EXTM3U\n"]
    sorted_channels = sorted(channel_groups.items(), key=lambda x: x[0])

    total_channels = 0
    total_urls = 0

    for channel_name, sources in sorted_channels:
        sources.sort(key=lambda x: x[0])

        for i, (priority, info_line, url, source_name) in enumerate(sources[:MAX_SOURCES_PER_CHANNEL]):
            source_tag = f"[{source_name}]"
            display_name = channel_name

            if len(sources) > 1:
                display_name = f"{channel_name} {source_tag}"

            new_info = re.sub(r',(.+)$', f',{display_name}', info_line)
            output_lines.append(f"{new_info}\n")
            output_lines.append(f"{url}\n")
            total_urls += 1

        total_channels += 1

    return "".join(output_lines), total_channels, total_urls


# ============ 主流程 ============

async def main():
    print("=" * 50)
    print("IPTV 智能聚合（运营商优先排序）")
    print("=" * 50)

    print(f"\n📥 下载源文件 (共{len(FILES)}个)...")
    connector = aiohttp.TCPConnector(limit=5)
    session = aiohttp.ClientSession(connector=connector)

    all_channels = []
    for fname in FILES:
        source_name = fname.replace('.m3u', '')
        content = await download_m3u(session, fname)
        if content:
            channels = parse_m3u(content, source_name)
            all_channels.extend(channels)
            print(f"    解析到 {len(channels)} 个频道")
        await asyncio.sleep(0.5)

    print(f"\n📊 共收集 {len(all_channels)} 个频道源")

    if not all_channels:
        print("❌ 没有获取到任何频道，退出")
        await session.close()
        return

    unique_channels = set(c[0] for c in all_channels)
    print(f"📊 涉及 {len(unique_channels)} 个不同频道")

    print("\n📝 生成聚合播放列表...")
    m3u_content, total_ch, total_url = build_optimized_m3u(all_channels)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(m3u_content)

    print(f"✅ 输出完成: {total_ch} 个频道, {total_url} 个源, 保存到 {OUTPUT_FILE}")
    print(f"📋 运营商优先级: {'电信' if MY_ISP == 'telecom' else '联通'}优先")

    await session.close()


if __name__ == "__main__":
    asyncio.run(main())