from __future__ import annotations

from html import escape


def build_swagger_html(api_base_url: str) -> str:
    escaped_api_base_url = escape(api_base_url, quote=True)
    return (
        """<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>miot-api-server docs</title>
    <link rel="stylesheet" href="/static/vendor/swagger-ui/swagger-ui.css" />
    <link rel="stylesheet" href="/static/docs/docs.css" />
  </head>
  <body data-api-base-url=\""""
        + escaped_api_base_url
        + """\">
    <div class="toolbar">
      <strong>miot-api-server Docs</strong>
      <input id="token-input" type="password" placeholder="输入 APP_TOKEN 后加载文档" />
      <button id="load-docs" type="button">加载文档</button>
      <button id="clear-token" type="button">清空 Token</button>
      <a href="/login">扫码登录页</a>
    </div>
    <div id="status" class="status"></div>
    <div id="swagger-ui"></div>
    <script src="/static/vendor/swagger-ui/swagger-ui-bundle.js"></script>
    <script src="/static/docs/swagger-docs.js"></script>
  </body>
</html>"""
    )


def build_redoc_html(api_base_url: str) -> str:
    escaped_api_base_url = escape(api_base_url, quote=True)
    return (
        """<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>miot-api-server redoc</title>
    <link rel="stylesheet" href="/static/docs/docs.css" />
  </head>
  <body data-api-base-url=\""""
        + escaped_api_base_url
        + """\">
    <div class="toolbar">
      <strong>miot-api-server ReDoc</strong>
      <input id="token-input" type="password" placeholder="输入 APP_TOKEN 后加载文档" />
      <button id="load-docs" type="button">加载文档</button>
      <a href="/login">扫码登录页</a>
    </div>
    <div id="status" class="status"></div>
    <div id="redoc-container"></div>
    <script src="/static/vendor/redoc/redoc.standalone.js"></script>
    <script src="/static/docs/redoc-docs.js"></script>
    </body>
</html>"""
    )
