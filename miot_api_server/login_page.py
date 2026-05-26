from __future__ import annotations

from html import escape

from miot_api_server.login_page_script import LOGIN_PAGE_SCRIPT
from miot_api_server.login_page_style import LOGIN_PAGE_STYLE


def build_login_html(api_base_url: str) -> str:
    escaped_api_base_url = escape(api_base_url, quote=True)
    return (
        """<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>miot-api-server login</title>
    <style>
"""
        + LOGIN_PAGE_STYLE
        + """
    </style>
  </head>
  <body data-api-base-url=\""""
        + escaped_api_base_url
        + """\">
    <main class="page">
      <section class="hero">
        <h1>米家登录与设备控制</h1>
        <p>这个页面把第一阶段最小闭环收口成一条自然路径：输入 <code>APP_TOKEN</code>，扫码登录米家账号，然后直接从设备列表里选择支持的能力进行控制。页面不通过 query string 传 token，所有请求仍然统一走 Bearer 头。</p>
        <div class="hero-links">
          <a href="/docs">打开 Swagger 文档</a>
          <a href="/redoc">打开 ReDoc</a>
        </div>
      </section>

      <section class="grid">
        <article class="panel">
          <h2>1. 准备 Token</h2>
          <p>这里的 token 就是启动服务时传入的 <code>APP_TOKEN</code>。页面只把它保存在当前浏览器会话里，便于后续继续访问文档页和设备控制接口。</p>
          <div class="field">
            <label for="token-input">APP_TOKEN</label>
            <input id="token-input" type="password" placeholder="输入 APP_TOKEN" />
          </div>
          <div class="actions">
            <button id="auth-status-button" type="button">查询登录状态</button>
            <button id="clear-token-button" type="button" class="secondary">清空 Token</button>
            <button id="reset-state-button" type="button" class="warning">重置测试状态</button>
          </div>
          <div class="meta">
            <div class="meta-row">
              <strong>当前认证状态</strong>
              <pre id="auth-status-output">尚未查询</pre>
            </div>
          </div>
          <div id="auth-status-message" class="status"></div>
        </article>

        <article class="panel">
          <h2>2. 开始扫码</h2>
          <p>点击“开始扫码登录”后，服务端会向米家登录流程申请二维码，并立即开始等待扫码确认。你可以直接扫页面里的二维码，也可以点击下方登录链接跳转。</p>
          <div class="actions">
            <button id="start-login-button" type="button">开始扫码登录</button>
          </div>
          <div class="meta">
            <div class="meta-row">
              <strong>登录会话 ID</strong>
              <code id="session-id-output">尚未创建</code>
            </div>
            <div class="meta-row">
              <strong>登录链接</strong>
              <code id="login-url-output">尚未创建</code>
            </div>
          </div>
          <div class="qr-box">
            <img id="qr-image" alt="二维码" hidden />
            <span id="qr-placeholder">点击上方按钮后，这里会显示二维码。</span>
          </div>
          <div id="start-login-message" class="status"></div>
        </article>

        <article class="panel">
          <h2>3. 等待扫码确认</h2>
          <p>页面会在生成二维码后立即进入等待状态，贴近底层库的原始登录流程。如果等待超时、网络中断或你想重试，可以手动再次点击下面按钮重新等待。</p>
          <div class="field">
            <label for="session-id-input">session_id</label>
            <input id="session-id-input" type="text" placeholder="开始扫码后会自动填入" />
          </div>
          <div class="field">
            <label for="timeout-input">timeout_seconds</label>
            <input id="timeout-input" type="number" min="1" max="180" value="120" />
          </div>
          <div class="actions">
            <button id="finish-login-button" type="button" class="warning">重新等待扫码确认</button>
          </div>
          <div class="meta">
            <div class="meta-row">
              <strong>登录结果</strong>
              <pre id="finish-login-output">尚未执行</pre>
            </div>
          </div>
          <div id="finish-login-message" class="status"></div>
          <ol class="hint-list">
            <li>如果页面提示已登录，就不用重复扫码。</li>
            <li>登录完成后，页面会自动加载设备列表与已支持的能力。</li>
            <li>如果等待超时或二维码失效，重新点击“开始扫码登录”即可生成新的会话。</li>
          </ol>
        </article>

        <article class="panel panel-wide">
          <h2>4. 设备与能力</h2>
          <p>当前页面只正式支持 `power` 能力。你可以直接从设备列表里选择设备并发起操作；页面也会为每个设备生成可切换的 curl / JS 示例代码，便于把页面联调结果转成脚本请求。</p>
          <div class="actions">
            <button id="refresh-devices-button" type="button" class="success">刷新设备列表</button>
          </div>
          <div id="devices-message" class="status"></div>
          <div id="devices-container" class="device-list">
            <div class="empty-state">登录完成后，这里会显示设备列表与当前已支持的控制能力。</div>
          </div>
        </article>
      </section>
    </main>
    <script>
"""
        + LOGIN_PAGE_SCRIPT
        + """
    </script>
  </body>
</html>"""
    )
