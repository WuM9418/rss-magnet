from flask import Flask, Response, request
from feedgen.feed import FeedGenerator
from urllib.parse import urlparse, parse_qs, unquote
from datetime import datetime, timezone
from bs4 import BeautifulSoup
import requests
import re
import logging
import json

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# 加载订阅源配置
with open("feeds.json", "r", encoding="utf-8") as f:
    FEEDS = json.load(f)

def extract_episode(raw_title):
    # 合集识别：如 01-26、全集、整季
    if re.search(r'\b\d{2,3}[-~_]\d{2,3}\b', raw_title):
        match = re.search(r'\b(\d{2,3})[-~_](\d{2,3})\b', raw_title)
        return f'合集 第{match.group(1)}-{match.group(2)}集'
    if any(keyword in raw_title for keyword in ['全集', '整季', '合集']):
        return '全集'

    # 单集识别：EP01、Vol02、[03]、第04话等
    match = re.search(r'(EP|Vol|第)?(\d{2,3})([话話集])?', raw_title)
    if match:
        return f'第{match.group(2)}集'

    return '未知集数'

@app.route('/rss/<name>')
def generate_rss(name):
    try:
        if name not in FEEDS:
            return Response(f"未找到订阅源: {name}", status=404)

        target_url = FEEDS[name]
        headers = {
            'User-Agent': 'Mozilla/5.0'
        }

        response = requests.get(target_url, headers=headers, timeout=10)
        response.encoding = response.apparent_encoding or 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)

        unique = {}
        for a in links:
            href = a['href']
            if href.startswith('magnet:?'):
                btih_match = re.search(r'btih:([a-fA-F0-9]+)', href)
                if btih_match:
                    btih = btih_match.group(1)
                    if btih not in unique:
                        link_text = a.text.strip()
                        params = parse_qs(urlparse(href).query)
                        dn_title = unquote(params.get('dn', [''])[0])
                        raw_title = link_text or dn_title or href

                        # 提取剧集编号（合集或单集）
                        episode = extract_episode(raw_title)

                        # 提取清晰度标签
                        quality_match = re.search(r'(720p|1080p|2160p|HD|BluRay)', raw_title, re.IGNORECASE)
                        quality = quality_match.group(1) if quality_match else ''

                        # 构造标题
                        title = f'{name} {episode}'
                        if quality:
                            title += f' {quality}'

                        unique[btih] = {
                            "title": title,
                            "link": href,
                            "guid": btih,
                            "pubDate": datetime.now(timezone.utc)
                        }

        if not unique:
            return Response("未找到有效磁力链接。", status=404)

        fg = FeedGenerator()
        fg.title(f'{name}磁力订阅')
        fg.link(href=request.url)
        fg.description(f'{name} 的磁力链接 RSS 订阅')
        fg.lastBuildDate(datetime.now(timezone.utc))

        for item in unique.values():
            fe = fg.add_entry()
            fe.title(item["title"])
            fe.link(href=item["link"])
            fe.guid(item["guid"])
            fe.enclosure(url=item["link"], type="application/x-bittorrent")
            fe.pubDate(item["pubDate"])

        rss_data = fg.rss_str(pretty=True).decode('utf-8')
        return Response(rss_data, content_type='application/rss+xml; charset=utf-8')

    except Exception as e:
        app.logger.error(f"{name} RSS生成失败: {e}")
        return Response(f"服务器错误: {e}", status=500)

@app.route('/')
def index():
    links = [f'<li><a href="/rss/{name}">{name}</a></li>' for name in FEEDS]
    return f'<h3>磁力RSS服务</h3><ul>{"".join(links)}</ul>'

@app.route('/health')
def health():
    return 'OK', 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
