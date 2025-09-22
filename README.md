# RSS Magnet 简介

🎬 这是一个小工具，可以把电影港的页面变成 RSS 订阅源，让你用下载工具（比如 ANI-RSS）自动下载资源。

## 🧐 为什么要做这个？

我一直在电影港找资源，但它不支持 RSS，RSShub 也没收录（有点意外）。所以我就自己动手，在Copilot的帮助下用 Docker 搭了这个服务。过程中踩了不少坑，尤其是 RSS 导入 ANI-RSS 时识别不了文件，调了好久才搞定（目前还是识别不了合集资源）。

## 🚀 怎么部署？

用 Docker 很简单，复制下面这段 `docker-compose.yml` 配置就能跑起来：

```yaml
services:
  rss-magnet:
    build: .
    container_name: rss-magnet
    ports:
      - "5000:5000"  # 可以改成你喜欢的端口
    restart: unless-stopped
    volumes:
      - .:/app       # 映射当前目录到容器里
    environment:
      - TZ=Asia/Taipei

```
📄 feeds.json 要怎么写？
这个文件是你想订阅的电影港页面列表，格式如下：

```yaml
{
  "师兄啊师兄": "https://www.dygangs.net/dmq/20230120/51294.htm",
  "吞噬星空": "https://www.dygang.cc/dmq/20201207/46020.htm",
  "仙逆": "https://www.dygang.cc/dmq/20230926/52997.htm"
}

```
✅ 注意：每个条目之间要用英文逗号分隔，别漏了！

📡 RSS 地址怎么用？
部署完成后，你可以通过下面的格式访问 RSS 源：

http://localhost:5000/rss/资源名称

比如：http://localhost:5000/rss/吞噬星空

这个链接可以直接导入到 ANI-RSS 等工具中进行订阅和自动下载。


