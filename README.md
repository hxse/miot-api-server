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

## Caddy 反代

推荐把网页入口和 API 入口拆成两个域名。网页域名套 Authelia；API 域名只透出 `/api/*`，由服务内部的 `Authorization: Bearer APP_TOKEN` 保护。

```caddy
miot.example.com {
  handle /api/* {
    reverse_proxy 127.0.0.1:6219
  }

  handle {
    import authelia_forward_auth
    reverse_proxy 127.0.0.1:6219
  }
}

miot-api.example.com {
  handle /api/* {
    reverse_proxy 127.0.0.1:6219
  }

  respond 404
}
```

应用内部不关心域名，也不做 CORS 配置；网页永远请求同源 `/api`。如果需要 API 域名给 curl 使用，只在 Caddy 层把同一组 `/api/*` 转发出去。
