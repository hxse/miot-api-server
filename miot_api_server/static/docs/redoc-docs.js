(() => {
  const storageKey = "miot_api_server_bearer_token";
  const tokenInput = document.getElementById("token-input");
  const statusBox = document.getElementById("status");
  const loadButton = document.getElementById("load-docs");
  const apiBaseUrl = document.body.dataset.apiBaseUrl || "/api";
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

    const response = await fetch(`${apiBaseUrl}/openapi.json`, {
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
    window.Redoc.init(spec, {}, document.getElementById("redoc-container"));
  }

  loadButton.addEventListener("click", () => {
    void loadDocs();
  });

  if (tokenInput.value.trim()) {
    void loadDocs();
  } else {
    setStatus("输入 APP_TOKEN 后才会加载 OpenAPI 文档内容。");
  }
})();
