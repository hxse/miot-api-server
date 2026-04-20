from __future__ import annotations


LOGIN_PAGE_EXAMPLE_SCRIPT = """
      const exampleTokenPlaceholder = "YOUR_APP_TOKEN";

      function resolvePowerPropertyName(device, selector) {
        const selected = selector.value.trim();
        if (selected) {
          return selected;
        }
        if (device.power.default_property_name) {
          return device.power.default_property_name;
        }
        return "YOUR_POWER_PROPERTY_NAME";
      }

      function buildCurlCommand(device, isOn, propertyName) {
        const body = JSON.stringify({ property_name: propertyName });
        const url = `${window.location.origin}/devices/${encodeURIComponent(device.did)}/power/${isOn ? "on" : "off"}`;
        // curl 示例统一使用占位 token，避免把浏览器会话里的真实 token 直接回显到页面。
        return `curl -X POST -H 'Authorization: Bearer ${exampleTokenPlaceholder}' -H 'Content-Type: application/json' -d '${body}' '${url}'`;
      }

      function buildJsCommand(device, isOn, propertyName) {
        const requestBody = `{ property_name: ${JSON.stringify(propertyName)} }`;
        const url = `${window.location.origin}/devices/${encodeURIComponent(device.did)}/power/${isOn ? "on" : "off"}`;
        // JS 示例与 curl 示例一样，统一使用占位 token，避免把真实 token 回显到页面。
        return [
          "(async () => {",
          `  const response = await fetch(${JSON.stringify(url)}, {`,
          '    method: "POST",',
          '    headers: {',
          `      "Authorization": "Bearer ${exampleTokenPlaceholder}",`,
          '      "Content-Type": "application/json",',
          "    },",
          `    body: JSON.stringify(${requestBody}),`,
          "  });",
          "  const result = await response.json();",
          "  console.log(result);",
          "})();",
        ].join("\\n");
      }

      function getExampleModeLabel(mode) {
        return mode === "js" ? "JS" : "curl";
      }

      function buildRequestExample(device, isOn, propertyName, mode) {
        if (mode === "js") {
          return buildJsCommand(device, isOn, propertyName);
        }
        return buildCurlCommand(device, isOn, propertyName);
      }

      function updateModeButtons(modeButtons, activeMode) {
        for (const [mode, button] of Object.entries(modeButtons)) {
          const isActive = mode === activeMode;
          button.classList.toggle("secondary", !isActive);
          button.classList.toggle("mode-button-active", isActive);
          button.setAttribute("aria-pressed", isActive ? "true" : "false");
        }
      }

      function createExampleCommandGroup(titleText) {
        const group = document.createElement("div");
        group.className = "example-command-group";
        const title = document.createElement("strong");
        title.textContent = titleText;
        const command = document.createElement("pre");
        command.className = "example-command";
        const copyButton = document.createElement("button");
        copyButton.type = "button";
        copyButton.className = "secondary";
        group.append(title, command, copyButton);
        return { group, title, command, copyButton };
      }
"""
