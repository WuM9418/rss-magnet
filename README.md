  很久以来一直在电影港下载资源，但是电影港不支持RSS，RSShub上也没有（还挺意外的）。但是不甘心就让Copilot帮忙部署了这个docker项目，来回改配置文件加测试折腾了好久，最主要解析完生成的RSS源导入ANI-RSS识别不到文件，修改了好久才解决（目前还是识别不了合集），但也算可用了。
采用docker-compose.yml部署

services:
  rss-magnet:
    build: .
    container_name: rss-magnet
    ports:
      - "5000:5000"  # 自己修改端口避免冲突
    restart: unless-stopped
    volumes:
      - .:/app  # ✅ 映射当前目录到容器内
    environment:
      - TZ=Asia/Taipei

      feeds.json文件为需要解析的电影港页面，以下为示例，修改时千万注意不要漏了那个分割用的逗号！！！

      
      {
  "师兄啊师兄": "https://www.dygangs.net/dmq/20230120/51294.htm",
  "吞噬星空": "https://www.dygang.cc/dmq/20201207/46020.htm",
  "仙逆": "https://www.dygang.cc/dmq/20230926/52997.htm"
}

部署后可以通过以下格式访问RSS源，此源可以直接导入ANI-RSS订阅下载。
示例：  http://localhost:5000/rss/吞噬星空
