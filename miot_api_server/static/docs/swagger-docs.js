(() => {
  const storageKey = "miot_api_server_bearer_token";
  const tokenInput = document.getElementById("token-input");
  const statusBox = document.getElementById("status");
  const loadButton = document.getElementById("load-docs");
  const clearButton = document.getElementById("clear-token");
  const swaggerContainer = document.getElementById("swagger-ui");
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

    window.SwaggerUIBundle({
      spec,
      dom_id: "#swagger-ui",
      validatorUrl: null,
      presets: [window.SwaggerUIBundle.presets.apis],
      layout: "BaseLayout",
      requestInterceptor: (request) => {
        request.headers = request.headers || {};
        request.headers.Authorization = `Bearer ${currentToken}`;
        return request;
      },
    });
  }

  loadButton.addEventListener("click", () => {
    void loadDocs();
  });
  clearButton.addEventListener("click", () => {
    currentToken = "";
    tokenInput.value = "";
    sessionStorage.removeItem(storageKey);
    swaggerContainer.replaceChildren();
    setStatus("已清空缓存的 token。");
  });

  if (currentToken) {
    void loadDocs();
  } else {
    setStatus("输入 APP_TOKEN 后才会加载 OpenAPI 文档内容。");
  }
})();
