from __future__ import annotations

from miot_api_server.login_page_examples_script import LOGIN_PAGE_EXAMPLE_SCRIPT

LOGIN_PAGE_SCRIPT = (
    """
      const tokenStorageKey = "miot_api_server_bearer_token";
      const sessionStorageKey = "miot_api_server_login_session_id";
      const tokenInput = document.getElementById("token-input");
      const authStatusButton = document.getElementById("auth-status-button");
      const clearTokenButton = document.getElementById("clear-token-button");
      const resetStateButton = document.getElementById("reset-state-button");
      const authStatusOutput = document.getElementById("auth-status-output");
      const authStatusMessage = document.getElementById("auth-status-message");
      const startLoginButton = document.getElementById("start-login-button");
      const sessionIdOutput = document.getElementById("session-id-output");
      const loginUrlOutput = document.getElementById("login-url-output");
      const qrImage = document.getElementById("qr-image");
      const qrPlaceholder = document.getElementById("qr-placeholder");
      const startLoginMessage = document.getElementById("start-login-message");
      const sessionIdInput = document.getElementById("session-id-input");
      const timeoutInput = document.getElementById("timeout-input");
      const finishLoginButton = document.getElementById("finish-login-button");
      const finishLoginOutput = document.getElementById("finish-login-output");
      const finishLoginMessage = document.getElementById("finish-login-message");
      const refreshDevicesButton = document.getElementById("refresh-devices-button");
      const devicesMessage = document.getElementById("devices-message");
      const devicesContainer = document.getElementById("devices-container");
      let finishInFlight = false;

      tokenInput.value = sessionStorage.getItem(tokenStorageKey) || "";
      sessionIdInput.value = sessionStorage.getItem(sessionStorageKey) || "";
      if (sessionIdInput.value.trim()) {
        sessionIdOutput.textContent = sessionIdInput.value.trim();
      }

      function setMessage(element, message, tone = "") {
        element.textContent = message;
        element.classList.toggle("success-text", tone === "success");
        element.classList.toggle("warning-text", tone === "warning");
      }

      async function copyText(text) {
        if (!navigator.clipboard || !navigator.clipboard.writeText) {
          throw new Error("当前浏览器不支持直接复制，请手动复制下方命令。");
        }
        await navigator.clipboard.writeText(text);
      }

      function requireToken() {
        const token = tokenInput.value.trim();
        if (!token) {
          throw new Error("APP_TOKEN 不能为空。");
        }
        sessionStorage.setItem(tokenStorageKey, token);
        return token;
      }

      function buildApiUrl(path) {
        return `/api${path}`;
      }

      function buildAbsoluteApiUrl(path) {
        return new URL(buildApiUrl(path), window.location.origin).toString();
      }

      function resetQrState(message = "点击上方按钮后，这里会显示二维码。") {
        qrImage.hidden = true;
        qrImage.style.display = "none";
        qrImage.src = "data:,";
        qrPlaceholder.hidden = false;
        qrPlaceholder.textContent = message;
      }

      function resetDevicesState(message) {
        devicesContainer.replaceChildren();
        const empty = document.createElement("div");
        empty.className = "empty-state";
        empty.textContent = message;
        devicesContainer.appendChild(empty);
      }

      function resetLoginUiState() {
        sessionStorage.removeItem(sessionStorageKey);
        sessionIdOutput.textContent = "尚未创建";
        loginUrlOutput.replaceChildren(document.createTextNode("尚未创建"));
        sessionIdInput.value = "";
        finishLoginOutput.textContent = "尚未执行";
        authStatusOutput.textContent = "尚未查询";
        setMessage(startLoginMessage, "");
        setMessage(finishLoginMessage, "");
        resetQrState("点击上方按钮后，这里会显示二维码。");
        resetDevicesState("登录完成后，这里会显示设备列表与当前已支持的控制能力。");
      }

      function renderLoginSession(data) {
        if (data.already_logged_in) {
          sessionStorage.removeItem(sessionStorageKey);
          sessionIdOutput.textContent = "当前账号已登录";
          loginUrlOutput.replaceChildren(document.createTextNode("无需重复创建"));
          sessionIdInput.value = "";
          resetQrState("当前账号已登录，无需显示二维码。");
          setMessage(startLoginMessage, "当前认证文件已经可用，无需再次扫码。", "success");
          return;
        }

        sessionStorage.setItem(sessionStorageKey, data.session_id);
        sessionIdOutput.textContent = data.session_id;
        sessionIdInput.value = data.session_id;
        const link = document.createElement("a");
        link.href = data.login_url;
        link.target = "_blank";
        link.rel = "noreferrer";
        link.textContent = data.login_url;
        loginUrlOutput.replaceChildren(link);
        qrImage.src = data.qr_data_url || data.qr_image_url;
        qrImage.hidden = false;
        qrImage.style.display = "block";
        qrPlaceholder.hidden = true;
        setMessage(startLoginMessage, "二维码已生成，页面会立即开始等待米家 App 扫码确认。", "success");
      }

      function setWaitingState(isWaiting) {
        finishInFlight = isWaiting;
        startLoginButton.disabled = isWaiting;
        finishLoginButton.disabled = isWaiting;
        authStatusButton.disabled = isWaiting;
        refreshDevicesButton.disabled = isWaiting;
      }

      async function apiRequest(path, method = "GET", payload = null) {
        const token = requireToken();
        const options = {
          method,
          headers: {
            Authorization: `Bearer ${token}`,
          },
        };
        if (payload !== null) {
          options.headers["Content-Type"] = "application/json";
          options.body = JSON.stringify(payload);
        }

        const response = await fetch(buildApiUrl(path), options);
        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
          const detail = data.detail || `HTTP ${response.status}`;
          throw new Error(detail);
        }
        return data;
      }

      async function loadAuthStatus() {
        setMessage(authStatusMessage, "");
        try {
          const data = await apiRequest("/auth/status");
          authStatusOutput.textContent = JSON.stringify(data, null, 2);
          setMessage(authStatusMessage, "登录状态查询成功。", "success");
          if (data.logged_in) {
            await loadDevices();
          } else {
            resetDevicesState("当前尚未登录米家账号，完成扫码后这里会自动加载设备列表。");
          }
        } catch (error) {
          setMessage(authStatusMessage, error.message);
        }
      }

      async function startLogin() {
        setMessage(startLoginMessage, "");
        setMessage(finishLoginMessage, "");
        try {
          const data = await apiRequest("/auth/login/start", "POST");
          renderLoginSession(data);
          if (!data.already_logged_in) {
            void finishLogin(true);
          } else {
            finishLoginOutput.textContent = JSON.stringify({ message: "当前认证文件已经可用" }, null, 2);
            await loadDevices();
          }
        } catch (error) {
          resetQrState("二维码生成失败，请稍后重试。");
          setMessage(startLoginMessage, error.message);
        }
      }

      async function finishLogin(autoStart = false) {
        if (finishInFlight) {
          return;
        }
        setMessage(finishLoginMessage, "");
        const sessionId = sessionIdInput.value.trim();
        if (!sessionId) {
          setMessage(finishLoginMessage, "session_id 不能为空。");
          return;
        }

        const timeoutSeconds = Number(timeoutInput.value);
        if (!Number.isInteger(timeoutSeconds) || timeoutSeconds < 1 || timeoutSeconds > 180) {
          setMessage(finishLoginMessage, "timeout_seconds 必须是 1 到 180 之间的整数。");
          return;
        }

        setWaitingState(true);
        setMessage(
          finishLoginMessage,
          autoStart ? "二维码已生成，正在等待米家 App 扫码确认。" : "正在重新等待米家 App 扫码确认。",
          "warning",
        );

        try {
          const data = await apiRequest("/auth/login/finish", "POST", {
            session_id: sessionId,
            timeout_seconds: timeoutSeconds,
          });
          finishLoginOutput.textContent = JSON.stringify(data, null, 2);
          setMessage(finishLoginMessage, "登录完成，认证文件已写入服务端。", "success");
          await loadAuthStatus();
        } catch (error) {
          setMessage(finishLoginMessage, error.message);
        } finally {
          setWaitingState(false);
        }
      }
"""
    + LOGIN_PAGE_EXAMPLE_SCRIPT
    + """

      function renderDeviceCard(device) {
        const card = document.createElement("article");
        card.className = "device-card";

        const top = document.createElement("div");
        top.className = "device-top";

        const titleBox = document.createElement("div");
        titleBox.className = "device-title";
        const title = document.createElement("h3");
        title.textContent = device.name;
        const didText = document.createElement("code");
        didText.textContent = `did: ${device.did}`;
        titleBox.append(title, didText);

        const meta = document.createElement("div");
        meta.className = "device-meta";
        const onlineBadge = document.createElement("span");
        onlineBadge.className = `badge ${device.is_online ? "online" : "offline"}`;
        onlineBadge.textContent = device.is_online ? "在线" : "离线";
        const powerBadge = document.createElement("span");
        powerBadge.className = `badge ${device.power.supported ? "power" : "no-power"}`;
        powerBadge.textContent = device.power.supported ? "支持 power" : "不支持 power";
        meta.append(onlineBadge, powerBadge);

        top.append(titleBox, meta);
        card.appendChild(top);

        const info = document.createElement("div");
        info.className = "device-info";
        info.textContent = `model: ${device.model} | home_id: ${device.home_id || "-"}`;
        card.appendChild(info);

        const capabilityBox = document.createElement("div");
        capabilityBox.className = "capability-box";
        if (!device.power.supported) {
          capabilityBox.textContent = "当前第一阶段只支持 power 能力；该设备没有识别到可安全控制的 power 属性。";
          card.appendChild(capabilityBox);
          return card;
        }

        const summary = document.createElement("div");
        summary.className = "capability-row";
        const capabilityLabel = document.createElement("span");
        capabilityLabel.textContent = "power 候选属性：";
        summary.appendChild(capabilityLabel);
        for (const candidate of device.power.candidates) {
          const tag = document.createElement("code");
          tag.textContent = candidate.name;
          summary.appendChild(tag);
        }
        capabilityBox.appendChild(summary);

        const selectorRow = document.createElement("div");
        selectorRow.className = "field";
        const selectorLabel = document.createElement("label");
        selectorLabel.textContent = "选择 power 属性";
        const selector = document.createElement("select");
        selector.dataset.selectionRequired = device.power.selection_required ? "true" : "false";
        if (device.power.selection_required) {
          const placeholder = document.createElement("option");
          placeholder.value = "";
          placeholder.textContent = "请选择一个 power 属性";
          selector.appendChild(placeholder);
        }
        for (const candidate of device.power.candidates) {
          const option = document.createElement("option");
          option.value = candidate.name;
          option.textContent = `${candidate.name} (${candidate.description})`;
          selector.appendChild(option);
        }
        if (device.power.default_property_name) {
          selector.value = device.power.default_property_name;
        }
        selectorRow.append(selectorLabel, selector);
        capabilityBox.appendChild(selectorRow);

        const actionRow = document.createElement("div");
        actionRow.className = "actions";
        const onButton = document.createElement("button");
        onButton.type = "button";
        onButton.textContent = "打开";
        const offButton = document.createElement("button");
        offButton.type = "button";
        offButton.className = "secondary";
        offButton.textContent = "关闭";
        actionRow.append(onButton, offButton);
        capabilityBox.appendChild(actionRow);

        const localStatus = document.createElement("div");
        localStatus.className = "status";
        capabilityBox.appendChild(localStatus);

        const exampleBox = document.createElement("div");
        exampleBox.className = "example-box";
        const exampleHint = document.createElement("p");
        exampleHint.textContent = "下面的示例代码已经带上当前设备 did，并统一使用占位 token `YOUR_APP_TOKEN`。默认显示 curl；点击 js 后会切换成 JS fetch 示例。复制后把占位 token 替换成真实 APP_TOKEN 即可执行；如果设备需要显式选择 power 属性，请先在上方选定。";
        exampleBox.appendChild(exampleHint);

        const modeSwitcher = document.createElement("div");
        modeSwitcher.className = "example-mode-switcher";
        const curlModeButton = document.createElement("button");
        curlModeButton.type = "button";
        curlModeButton.textContent = "curl";
        const jsModeButton = document.createElement("button");
        jsModeButton.type = "button";
        jsModeButton.className = "secondary";
        jsModeButton.textContent = "js";
        modeSwitcher.append(curlModeButton, jsModeButton);
        exampleBox.appendChild(modeSwitcher);

        let exampleMode = "curl";
        const modeButtons = { curl: curlModeButton, js: jsModeButton };
        const onExampleGroup = createExampleCommandGroup("打开设备 curl 示例");
        const offExampleGroup = createExampleCommandGroup("关闭设备 curl 示例");
        onExampleGroup.copyButton.textContent = "复制打开示例";
        offExampleGroup.copyButton.textContent = "复制关闭示例";
        exampleBox.append(onExampleGroup.group, offExampleGroup.group);

        const exampleStatus = document.createElement("div");
        exampleStatus.className = "status";
        exampleBox.appendChild(exampleStatus);
        capabilityBox.appendChild(exampleBox);

        function refreshRequestExamples() {
          const propertyName = resolvePowerPropertyName(device, selector);
          const modeLabel = getExampleModeLabel(exampleMode);
          onExampleGroup.title.textContent = `打开设备 ${modeLabel} 示例`;
          offExampleGroup.title.textContent = `关闭设备 ${modeLabel} 示例`;
          onExampleGroup.command.textContent = buildRequestExample(device, true, propertyName, exampleMode);
          offExampleGroup.command.textContent = buildRequestExample(device, false, propertyName, exampleMode);
          updateModeButtons(modeButtons, exampleMode);
          if (selector.dataset.selectionRequired === "true" && !selector.value.trim()) {
            setMessage(exampleStatus, `该设备存在多个 power 候选属性；复制 ${modeLabel} 示例前请先在上方选择具体属性。`, "warning");
          } else {
            setMessage(exampleStatus, `${modeLabel} 示例已更新，可以直接复制。`, "success");
          }
        }

        async function controlPower(isOn) {
          const propertyName = selector.value.trim();
          if (selector.dataset.selectionRequired === "true" && !propertyName) {
            setMessage(localStatus, "该设备存在多个 power 候选属性，请先选择一个属性。");
            return;
          }

          onButton.disabled = true;
          offButton.disabled = true;
          setMessage(localStatus, isOn ? "正在打开设备..." : "正在关闭设备...", "warning");
          try {
            const payload = propertyName ? { property_name: propertyName } : null;
            const result = await apiRequest(
              `/devices/${encodeURIComponent(device.did)}/power/${isOn ? "on" : "off"}`,
              "POST",
              payload,
            );
            setMessage(localStatus, `${result.name} 已${isOn ? "打开" : "关闭"}，使用属性 ${result.power_property_name}。`, "success");
            setMessage(devicesMessage, "设备控制成功。", "success");
          } catch (error) {
            setMessage(localStatus, error.message);
            setMessage(devicesMessage, error.message);
          } finally {
            onButton.disabled = false;
            offButton.disabled = false;
          }
        }

        onButton.addEventListener("click", () => { void controlPower(true); });
        offButton.addEventListener("click", () => { void controlPower(false); });
        curlModeButton.addEventListener("click", () => {
          exampleMode = "curl";
          refreshRequestExamples();
        });
        jsModeButton.addEventListener("click", () => {
          exampleMode = "js";
          refreshRequestExamples();
        });
        selector.addEventListener("change", refreshRequestExamples);
        onExampleGroup.copyButton.addEventListener("click", async () => {
          try {
            await copyText(onExampleGroup.command.textContent);
            setMessage(exampleStatus, `打开设备 ${getExampleModeLabel(exampleMode)} 示例已复制到剪贴板。`, "success");
          } catch (error) {
            setMessage(exampleStatus, error.message);
          }
        });
        offExampleGroup.copyButton.addEventListener("click", async () => {
          try {
            await copyText(offExampleGroup.command.textContent);
            setMessage(exampleStatus, `关闭设备 ${getExampleModeLabel(exampleMode)} 示例已复制到剪贴板。`, "success");
          } catch (error) {
            setMessage(exampleStatus, error.message);
          }
        });
        refreshRequestExamples();

        card.appendChild(capabilityBox);
        return card;
      }

      async function loadDevices() {
        setMessage(devicesMessage, "");
        devicesContainer.replaceChildren();
        const loading = document.createElement("div");
        loading.className = "empty-state";
        loading.textContent = "正在加载设备列表...";
        devicesContainer.appendChild(loading);

        try {
          const devices = await apiRequest("/devices");
          devicesContainer.replaceChildren();
          if (!devices.length) {
            resetDevicesState("当前账号下没有可见设备。");
            return;
          }
          for (const device of devices) {
            devicesContainer.appendChild(renderDeviceCard(device));
          }
          setMessage(devicesMessage, "设备列表加载成功。", "success");
        } catch (error) {
          resetDevicesState(`设备列表加载失败：${error.message}`);
          setMessage(devicesMessage, error.message);
        }
      }

      authStatusButton.addEventListener("click", () => { void loadAuthStatus(); });
      startLoginButton.addEventListener("click", () => { void startLogin(); });
      finishLoginButton.addEventListener("click", () => { void finishLogin(false); });
      refreshDevicesButton.addEventListener("click", () => { void loadDevices(); });
      clearTokenButton.addEventListener("click", () => {
        tokenInput.value = "";
        sessionStorage.removeItem(tokenStorageKey);
        resetLoginUiState();
        resetDevicesState("浏览器会话中的 token 已清空。重新输入 token 并登录后，这里会重新显示设备列表。");
        setMessage(authStatusMessage, "已清空浏览器会话中的 token。", "success");
      });
      resetStateButton.addEventListener("click", async () => {
        if (finishInFlight) {
          setMessage(finishLoginMessage, "当前仍在等待扫码确认，请等待结束后再重置。");
          return;
        }

        const token = tokenInput.value.trim();
        if (!token) {
          sessionStorage.removeItem(tokenStorageKey);
          resetLoginUiState();
          setMessage(authStatusMessage, "已清空浏览器中的本地测试状态。若要清理服务端登录状态，请先输入 APP_TOKEN。", "warning");
          return;
        }

        try {
          const result = await apiRequest("/auth/reset", "POST");
          tokenInput.value = "";
          sessionStorage.removeItem(tokenStorageKey);
          resetLoginUiState();
          setMessage(
            authStatusMessage,
            `已重置测试状态：auth_file_deleted=${result.auth_file_deleted}，pending_login_sessions_cleared=${result.pending_login_sessions_cleared}。`,
            "success",
          );
        } catch (error) {
          setMessage(authStatusMessage, error.message);
        }
      });

      resetQrState();
      if (tokenInput.value.trim()) {
        void loadAuthStatus();
      }
"""
)
