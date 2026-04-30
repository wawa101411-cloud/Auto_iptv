import asyncio
import aiohttp
import re
import sys
from collections import defaultdict

# ============ 配置区 ============

# 源仓库CDN地址
BASE_URL = "https://gcore.jsdelivr.net/gh/Wang963963/IPTV-4K-M3U@main/m3u/"

# 所有线路列表
FILES = [
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
    "陕西电信1.m3u",
    "黑龙江联通.m3u",
]

# 测速配置
CONCURRENCY = 50
TIMEOUT = 8
MAX_SOURCES_PER_CHANNEL = 3

# 输出文件
OUTPUT_FILE = "auto_iptv_wang.m3u"


# ============ 下载与解析 ============

async def download_m3u(session, url):
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=20)) as resp:
            if resp.status == 200:
                text = await resp.text()
                print(f"  ✓ 下载成功: {url.split('/')[-1]}")
                return text
            else:
                print(f"  ✗ 下载失败({resp.status}): {url.split('/')[-1]}")
                return None
    except Exception as e:
        print(f"  ✗ 下载异常: {url.split('/')[-1]} - {e}")
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


# ============ 测速 ============

async def test_speed(session, url):
    try:
        start = asyncio.get_event_loop().time()
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=TIMEOUT)) as resp:
            if resp.status == 200:
                await resp.read(4096)
                latency = (asyncio.get_event_loop().time() - start) * 1000
                return (url, True, latency)
            else:
                return (url, False, -1)
    except Exception:
        return (url, False, -1)


async def batch_test_speed(urls_with_info):
    semaphore = asyncio.Semaphore(CONCURRENCY)
    results = []

    async def limited_test(item):
        url, channel_name, info_line, source_name = item
        async with semaphore:
            result_url, alive, latency = await test_speed(session_global, url)
            return (channel_name, info_line, url, source_name, alive, latency)

    tasks = [limited_test(item) for item in urls_with_info]
    completed = await asyncio.gather(*tasks)

    alive_count = sum(1 for r in completed if r[4])
    total_count = len(completed)
    print(f"\n测速完成: {alive_count}/{total_count} 个源可用")

    return completed


# ============ 排序与输出 ============

def build_optimized_m3u(test_results):
    channel_groups = defaultdict(list)
    for channel_name, info_line, url, source_name, alive, latency in test_results:
        if alive:
            channel_groups[channel_name].append({
                'info': info_line,
                'url': url,
                'source': source_name,
                'latency': latency
            })

    output_lines = ["#EXTM3U\n"]
    sorted_channels = sorted(channel_groups.items(), key=lambda x: x[0])

    for channel_name, sources in sorted_channels:
        sources.sort(key=lambda x: x['latency'])

        for i, src in enumerate(sources[:MAX_SOURCES_PER_CHANNEL]):
            latency_str = f"{src['latency']:.0f}ms"
            source_tag = f"[{src['source']}]"

            if len(sources) > 1 and i > 0:
                display_name = f"{channel_name}_{i+1}"
            else:
                display_name = channel_name

            new_info = re.sub(
                r',(.+)$',
                f',{display_name} {source_tag}{latency_str}',
                src['info']
            )

            output_lines.append(f"{new_info}\n")
            output_lines.append(f"{src['url']}\n")

    return "".join(output_lines)


# ============ 主流程 ============

async def main():
    global session_global

    print("=" * 50)
    print("IPTV 自动测速择优")
    print("=" * 50)

    print(f"\n📥 下载源文件 (共{len(FILES)}个)...")
    connector = aiohttp.TCPConnector(limit=20)
    session_global = aiohttp.ClientSession(connector=connector)

    all_channels = []
    for fname in FILES:
        url = BASE_URL + fname
        source_name = fname.replace('.m3u', '')
        content = await download_m3u(session_global, url)
        if content:
            channels = parse_m3u(content, source_name)
            all_channels.extend(channels)
            print(f"    解析到 {len(channels)} 个频道")

    print(f"\n📊 共收集 {len(all_channels)} 个频道源")

    if not all_channels:
        print("❌ 没有获取到任何频道，退出")
        await session_global.close()
        return

    unique_channels = set(c[0] for c in all_channels)
    print(f"📊 涉及 {len(unique_channels)} 个不同频道")

    print(f"\n🚀 开始测速 (并发={CONCURRENCY}, 超时={TIMEOUT}s)...")
    urls_with_info = [(url, name, info, src) for name, info, url, src in all_channels]
    test_results = await batch_test_speed(urls_with_info)

    print("\n📝 生成最优播放列表...")
    m3u_content = build_optimized_m3u(test_results)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(m3u_content)

    result_channels = defaultdict(list)
    for name, info, url, src, alive, latency in test_results:
        if alive:
            result_channels[name].append(latency)
    print(f"✅ 输出完成: {len(result_channels)} 个频道, 保存到 {OUTPUT_FILE}")

    print("\n📊 部分频道最快源统计:")
    for name in sorted(result_channels.keys())[:20]:
        fastest = min(result_channels[name])
        count = len(result_channels[name])
        print(f"  {name}: 最快 {fastest:.0f}ms, 共 {count} 个可用源")
    if len(result_channels) > 20:
        print(f"  ... 还有 {len(result_channels) - 20} 个频道")

    await session_global.close()


if __name__ == "__main__":
    asyncio.run(main())