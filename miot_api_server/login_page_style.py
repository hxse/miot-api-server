from __future__ import annotations


LOGIN_PAGE_STYLE = """
      :root {
        --bg: #f3f4f6;
        --panel: #ffffff;
        --border: #d1d5db;
        --text: #111827;
        --muted: #4b5563;
        --primary: #2563eb;
        --danger: #dc2626;
        --success: #15803d;
        --warning: #b45309;
      }
      * { box-sizing: border-box; }
      body {
        margin: 0;
        font-family: "Noto Sans SC", "PingFang SC", sans-serif;
        color: var(--text);
        background:
          radial-gradient(circle at top left, #dbeafe 0, transparent 28%),
          radial-gradient(circle at right, #fde68a 0, transparent 24%),
          var(--bg);
      }
      .page {
        max-width: 1180px;
        margin: 0 auto;
        padding: 32px 20px 48px;
      }
      .hero {
        display: grid;
        gap: 16px;
        margin-bottom: 24px;
      }
      .hero h1 {
        margin: 0;
        font-size: 36px;
        line-height: 1.1;
      }
      .hero p {
        margin: 0;
        max-width: 860px;
        color: var(--muted);
        line-height: 1.6;
      }
      .hero-links {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
      }
      .hero-links a {
        color: var(--primary);
        text-decoration: none;
        font-weight: 600;
      }
      .grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
        gap: 20px;
      }
      .panel {
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 16px 40px rgba(15, 23, 42, 0.08);
      }
      .panel-wide {
        grid-column: 1 / -1;
      }
      .panel h2 {
        margin: 0 0 14px;
        font-size: 22px;
      }
      .panel p {
        margin: 0 0 16px;
        color: var(--muted);
        line-height: 1.6;
      }
      .field {
        display: grid;
        gap: 8px;
        margin-bottom: 14px;
      }
      .field label {
        font-weight: 600;
      }
      .field input,
      .field select {
        width: 100%;
        padding: 12px 14px;
        border: 1px solid var(--border);
        border-radius: 12px;
        background: #fff;
        font-size: 15px;
      }
      .actions {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin-top: 14px;
      }
      button {
        display: inline-flex;
        flex: 0 0 auto;
        align-items: center;
        justify-content: center;
        border: none;
        border-radius: 12px;
        background: var(--primary);
        color: white;
        min-height: 40px;
        min-width: 96px;
        padding: 9px 22px;
        font-size: 15px;
        font-weight: 600;
        line-height: 1.2;
        white-space: nowrap;
        cursor: pointer;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08);
        transition:
          transform 140ms ease,
          box-shadow 160ms ease,
          background-color 160ms ease,
          color 160ms ease,
          filter 160ms ease;
      }
      button.secondary {
        background: #e5e7eb;
        color: var(--text);
      }
      button.success {
        background: var(--success);
      }
      button.warning {
        background: var(--warning);
      }
      button:disabled {
        opacity: 0.55;
        cursor: not-allowed;
        box-shadow: none;
      }
      button:not(:disabled):not(.mode-button-active):hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(15, 23, 42, 0.14);
      }
      button:not(:disabled):not(.mode-button-active):active {
        transform: translateY(0);
        box-shadow:
          inset 0 0 0 999px rgba(255, 255, 255, 0.08),
          0 2px 6px rgba(15, 23, 42, 0.12);
      }
      button:focus-visible {
        outline: none;
        box-shadow:
          0 0 0 3px rgba(37, 99, 235, 0.2),
          0 6px 16px rgba(15, 23, 42, 0.12);
      }
      .status {
        min-height: 24px;
        margin-top: 14px;
        color: var(--danger);
        font-weight: 600;
      }
      .success-text {
        color: var(--success);
      }
      .warning-text {
        color: var(--warning);
      }
      .meta {
        display: grid;
        gap: 10px;
        margin-top: 16px;
      }
      .meta-row {
        display: grid;
        gap: 6px;
      }
      .meta-row strong {
        font-size: 14px;
      }
      .meta-row code,
      .meta-row pre {
        margin: 0;
        padding: 12px;
        background: #f9fafb;
        border: 1px solid var(--border);
        border-radius: 12px;
        overflow-x: auto;
      }
      .qr-box {
        display: grid;
        place-items: center;
        min-height: 280px;
        border: 1px dashed var(--border);
        border-radius: 18px;
        background: #f9fafb;
        overflow: hidden;
      }
      .qr-box img {
        max-width: 100%;
        height: auto;
        display: block;
      }
      .hint-list {
        margin: 16px 0 0;
        padding-left: 18px;
        color: var(--muted);
        line-height: 1.7;
      }
      .device-list {
        display: grid;
        gap: 16px;
        margin-top: 16px;
      }
      .device-card {
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 16px;
        background: #f9fafb;
      }
      .device-top {
        display: flex;
        gap: 12px;
        justify-content: space-between;
        align-items: flex-start;
        flex-wrap: wrap;
      }
      .device-title {
        display: grid;
        gap: 6px;
      }
      .device-title h3 {
        margin: 0;
        font-size: 18px;
      }
      .device-meta {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
      }
      .badge {
        display: inline-flex;
        align-items: center;
        padding: 6px 10px;
        border-radius: 999px;
        background: #e5e7eb;
        color: var(--text);
        font-size: 12px;
        font-weight: 600;
      }
      .badge.online { background: #dcfce7; color: #166534; }
      .badge.offline { background: #fee2e2; color: #991b1b; }
      .badge.power { background: #dbeafe; color: #1d4ed8; }
      .badge.no-power { background: #f3f4f6; color: #6b7280; }
      .device-info {
        margin-top: 14px;
        color: var(--muted);
        line-height: 1.6;
      }
      .capability-box {
        display: grid;
        gap: 12px;
        margin-top: 16px;
        padding: 14px;
        border-radius: 14px;
        background: #fff;
        border: 1px solid var(--border);
      }
      .capability-row {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        align-items: center;
      }
      .capability-row code {
        padding: 6px 8px;
        border-radius: 10px;
        background: #f3f4f6;
        border: 1px solid var(--border);
      }
      .example-box {
        display: grid;
        gap: 12px;
        padding-top: 4px;
      }
      .example-box p {
        margin: 0;
        color: var(--muted);
        line-height: 1.6;
      }
      .example-mode-switcher {
        display: inline-flex;
        gap: 2px;
        flex-wrap: nowrap;
        align-items: center;
        padding: 3px;
        border: 1px solid #d5dde8;
        border-radius: 999px;
        background: #e7edf4;
        box-shadow: inset 0 1px 1px rgba(15, 23, 42, 0.05);
      }
      .example-mode-switcher button {
        min-width: 64px;
        min-height: 32px;
        padding: 6px 16px;
        border-radius: 999px;
        border: none;
        background: transparent;
        color: #66758a;
        box-shadow: none;
        font-weight: 700;
        transition:
          background-color 140ms ease,
          color 140ms ease,
          border-color 140ms ease,
          box-shadow 140ms ease;
      }
      .example-mode-switcher button:hover,
      .example-mode-switcher button:active,
      .example-mode-switcher button:focus-visible {
        transform: none;
      }
      .example-mode-switcher button:focus-visible {
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.18);
      }
      .example-mode-switcher button.secondary {
        background: transparent;
        color: #66758a;
      }
      .example-mode-switcher button.mode-button-active,
      .example-mode-switcher button.mode-button-active.secondary {
        background: #ffffff;
        color: #1d4ed8;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.12);
      }
      .example-command-group {
        display: grid;
        gap: 8px;
      }
      .example-command-group strong {
        font-size: 14px;
      }
      .example-command {
        margin: 0;
        padding: 14px;
        border-radius: 12px;
        border: 1px solid var(--border);
        background: #111827;
        color: #f9fafb;
        overflow-x: auto;
        white-space: pre-wrap;
        word-break: break-word;
        line-height: 1.6;
      }
      .empty-state {
        padding: 18px;
        border-radius: 16px;
        border: 1px dashed var(--border);
        color: var(--muted);
        background: #fff;
      }
      @media (max-width: 640px) {
        .page {
          padding: 24px 14px 40px;
        }
        .hero h1 {
          font-size: 28px;
        }
      }
"""
