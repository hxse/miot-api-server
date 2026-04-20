# miot-api-server

基于 `mijiaAPI` 的轻量 `FastAPI` 封装，用于通过 HTTP 控制米家设备。

## VPS 部署

默认从主分支拉取：

```bash
git clone https://github.com/hxse/miot-api-server
cd miot-api-server
docker build -t miot-api-server:local .
docker run -d \
  --name miot-api-server \
  --restart unless-stopped \
  -p 6219:8000 \
  -e APP_TOKEN='your-token' \
  -v miot-api-server-data:/data/mijia \
  miot-api-server:local
curl http://127.0.0.1:6219/healthz
```

如果只想部署当前 backup 分支，使用下面这组命令：

```bash
git clone -b backup --single-branch https://github.com/hxse/miot-api-server
cd miot-api-server
docker build -t miot-api-server:local .
docker run -d \
  --name miot-api-server \
  --restart unless-stopped \
  -p 6219:8000 \
  -e APP_TOKEN='your-token' \
  -v miot-api-server-data:/data/mijia \
  miot-api-server:local
curl http://127.0.0.1:6219/healthz
```
