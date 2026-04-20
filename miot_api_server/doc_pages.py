from __future__ import annotations


def build_swagger_html() -> str:
    return """<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>miot-api-server docs</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css" />
    <style>
      body { margin: 0; font-family: sans-serif; background: #f5f5f5; }
      .toolbar { display: flex; gap: 12px; align-items: center; padding: 16px; background: #111827; color: #f9fafb; }
      .toolbar input { flex: 1; min-width: 240px; padding: 10px 12px; border-radius: 8px; border: none; }
      .toolbar button { padding: 10px 14px; border: none; border-radius: 8px; background: #2563eb; color: white; cursor: pointer; }
      .toolbar a { color: #bfdbfe; text-decoration: none; font-size: 14px; }
      .status { padding: 0 16px 12px; color: #dc2626; background: #111827; }
      #swagger-ui { max-width: 1200px; margin: 0 auto; }
    </style>
  </head>
  <body>
    <div class="toolbar">
      <strong>miot-api-server Docs</strong>
      <input id="token-input" type="password" placeholder="输入 APP_TOKEN 后加载文档" />
      <button id="load-docs" type="button">加载文档</button>
      <button id="clear-token" type="button">清空 Token</button>
      <a href="/login">扫码登录页</a>
    </div>
    <div id="status" class="status"></div>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
      const storageKey = "miot_api_server_bearer_token";
      const tokenInput = document.getElementById("token-input");
      const statusBox = document.getElementById("status");
      const loadButton = document.getElementById("load-docs");
      const clearButton = document.getElementById("clear-token");
      let currentToken = sessionStorage.getItem(storageKey) || "";

      tokenInput.value = currentToken;

      function setStatus(message) {
        statusBox.textContent = message;
      }

      async function loadDocs() {
        const token = tokenInput.value.trim();
        if (!token) {
          setStatus("APP_TOKEN 不能为空。");
          return;
        }

        const response = await fetch("/openapi.json", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          setStatus(`文档加载失败：HTTP ${response.status}`);
          return;
        }

        const spec = await response.json();
        currentToken = token;
        sessionStorage.setItem(storageKey, token);
        setStatus("");

        SwaggerUIBundle({
          spec,
          dom_id: "#swagger-ui",
          presets: [SwaggerUIBundle.presets.apis],
          layout: "BaseLayout",
          requestInterceptor: (request) => {
            request.headers = request.headers || {};
            request.headers.Authorization = `Bearer ${currentToken}`;
            return request;
          },
        });
      }

      loadButton.addEventListener("click", loadDocs);
      clearButton.addEventListener("click", () => {
        currentToken = "";
        tokenInput.value = "";
        sessionStorage.removeItem(storageKey);
        document.getElementById("swagger-ui").innerHTML = "";
        setStatus("已清空缓存的 token。");
      });

      if (currentToken) {
        loadDocs();
      } else {
        setStatus("输入 APP_TOKEN 后才会加载 OpenAPI 文档内容。");
      }
    </script>
  </body>
</html>"""


def build_redoc_html() -> str:
    return """<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>miot-api-server redoc</title>
    <style>
      body { margin: 0; font-family: sans-serif; background: #f5f5f5; }
      .toolbar { display: flex; gap: 12px; align-items: center; padding: 16px; background: #111827; color: #f9fafb; }
      .toolbar input { flex: 1; min-width: 240px; padding: 10px 12px; border-radius: 8px; border: none; }
      .toolbar button { padding: 10px 14px; border: none; border-radius: 8px; background: #2563eb; color: white; cursor: pointer; }
      .toolbar a { color: #bfdbfe; text-decoration: none; font-size: 14px; }
      .status { padding: 0 16px 12px; color: #dc2626; background: #111827; }
      #redoc-container { min-height: calc(100vh - 96px); }
    </style>
  </head>
  <body>
    <div class="toolbar">
      <strong>miot-api-server ReDoc</strong>
      <input id="token-input" type="password" placeholder="输入 APP_TOKEN 后加载文档" />
      <button id="load-docs" type="button">加载文档</button>
      <a href="/login">扫码登录页</a>
    </div>
    <div id="status" class="status"></div>
    <div id="redoc-container"></div>
    <script src="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"></script>
    <script>
      const storageKey = "miot_api_server_bearer_token";
      const tokenInput = document.getElementById("token-input");
      const statusBox = document.getElementById("status");
      const loadButton = document.getElementById("load-docs");
      tokenInput.value = sessionStorage.getItem(storageKey) || "";

      function setStatus(message) {
        statusBox.textContent = message;
      }

      async function loadDocs() {
        const token = tokenInput.value.trim();
        if (!token) {
          setStatus("APP_TOKEN 不能为空。");
          return;
        }

        const response = await fetch("/openapi.json", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          setStatus(`文档加载失败：HTTP ${response.status}`);
          return;
        }

        const spec = await response.json();
        sessionStorage.setItem(storageKey, token);
        setStatus("");
        Redoc.init(spec, {}, document.getElementById("redoc-container"));
      }

      loadButton.addEventListener("click", loadDocs);

      if (tokenInput.value.trim()) {
        loadDocs();
      } else {
        setStatus("输入 APP_TOKEN 后才会加载 OpenAPI 文档内容。");
      }
    </script>
  </body>
</html>"""
