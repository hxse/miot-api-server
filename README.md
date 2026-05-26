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
  -e MIOT_API_BASE_URL='https://miot-api.hxse.top/api' \
  -e MIOT_CORS_ALLOWED_ORIGINS='https://miot.hxse.top' \
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
  -e MIOT_API_BASE_URL='https://miot-api.hxse.top/api' \
  -e MIOT_CORS_ALLOWED_ORIGINS='https://miot.hxse.top' \
  -v miot-api-server-data:/data/mijia \
  miot-api-server:local
curl http://127.0.0.1:6219/healthz
```

## Caddy 反代

推荐把网页入口和 API 入口拆成两个域名。网页域名套 Authelia；API 域名只透出 `/api/*`，由服务内部的 `Authorization: Bearer APP_TOKEN` 保护。

```caddy
miot.hxse.top {
  import authelia_forward_auth
  reverse_proxy 127.0.0.1:6219
}

miot-api.hxse.top {
  handle /api/* {
    reverse_proxy 127.0.0.1:6219
  }

  respond 404
}
```

网页会请求 `MIOT_API_BASE_URL`；跨域请求需要把网页域名写入 `MIOT_CORS_ALLOWED_ORIGINS`。本地调试不设置这两个变量时，默认使用同源 `/api`。
