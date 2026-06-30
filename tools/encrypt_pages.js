const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const crypto = require("crypto");

const password = process.env.DASHBOARD_PASSWORD;
if (!password) {
  console.error("Missing DASHBOARD_PASSWORD environment variable.");
  process.exit(1);
}

const root = path.resolve(__dirname, "..");
const sourcePages = [
  {
    id: "single2026",
    title: "2026年累计贡献分析",
    eyebrow: "",
    subtitle: "销量、销额、净边贡的同比增减，渠道 产品 区域 变化",
    href: "./",
    source: "F:\\llqdocument\\大成文件\\客户贡献分析\\2026年1-5月数据分析仪表盘.html",
    output: path.join(root, "index.html"),
    defaultRoute: "single2026",
    facts: [],
  },
  {
    id: "yoy",
    title: "2026 vs 2025 同比分析",
    eyebrow: "",
    subtitle: "销量、销额、净边贡的同比增减，渠道 产品 区域 变化",
    href: "./2026-dashboard.html",
    source: "F:\\llqdocument\\大成文件\\客户贡献分析\\26年与25年_1-5月数据对比分析.html",
    output: path.join(root, "2026-dashboard.html"),
    defaultRoute: "yoy",
    facts: [],
  },
];

function b64(buffer) {
  return Buffer.from(buffer).toString("base64");
}

function encryptBuffer(buffer) {
  const compressed = zlib.gzipSync(buffer, { level: 9 });
  const salt = crypto.randomBytes(16);
  const iv = crypto.randomBytes(12);
  const iterations = 310000;
  const key = crypto.pbkdf2Sync(password, salt, iterations, 32, "sha256");
  const cipher = crypto.createCipheriv("aes-256-gcm", key, iv);
  const encrypted = Buffer.concat([cipher.update(compressed), cipher.final()]);
  return {
    kdf: "PBKDF2-SHA256",
    cipher: "AES-256-GCM",
    compression: "gzip",
    iterations,
    salt: b64(salt),
    iv: b64(iv),
    tag: b64(cipher.getAuthTag()),
    data: b64(encrypted),
    originalBytes: buffer.length,
    gzipBytes: compressed.length,
  };
}

const encryptedPages = sourcePages.map((page) => {
  const plain = fs.readFileSync(page.source);
  const encrypted = encryptBuffer(plain);
  console.log(`${page.id}: encrypted ${encrypted.originalBytes} bytes, gzip ${encrypted.gzipBytes} bytes`);
  return {
    id: page.id,
    title: page.title,
    eyebrow: page.eyebrow,
    subtitle: page.subtitle,
    href: page.href,
    facts: page.facts,
    encrypted,
  };
});

for (const page of sourcePages) {
  const html = buildPortalShell({
    defaultRoute: page.defaultRoute,
    generatedAt: new Date().toISOString(),
    pages: encryptedPages,
  });
  fs.writeFileSync(page.output, html, "utf8");
  console.log(`${page.output} <= portal shell`);
}

function buildPortalShell(payload) {
  return `<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PFS销售数据分析平台</title>
  <style>
    :root {
      color-scheme: light;
      --ink: #09213f;
      --muted: #60738c;
      --line: #d8e3ef;
      --panel: rgba(255, 255, 255, .9);
      --brand: #1258b8;
      --brand-2: #00866f;
      --danger: #bb3b35;
      --shadow: 0 24px 70px rgba(8, 31, 61, .14);
      font-family: "Segoe UI", "Microsoft YaHei", "PingFang SC", sans-serif;
      background: #eef4fb;
      color: var(--ink);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      background:
        linear-gradient(90deg, rgba(18, 88, 184, .07) 1px, transparent 1px),
        linear-gradient(0deg, rgba(18, 88, 184, .06) 1px, transparent 1px),
        radial-gradient(circle at 12% 14%, rgba(18, 88, 184, .18), transparent 30%),
        radial-gradient(circle at 88% 18%, rgba(0, 134, 111, .15), transparent 30%),
        linear-gradient(135deg, #f8fbff 0%, #edf4fb 46%, #e8f0f8 100%);
      background-size: 42px 42px, 42px 42px, auto, auto, auto;
    }
    .page {
      width: min(1180px, calc(100vw - 36px));
      min-height: 100vh;
      margin: 0 auto;
      padding: 32px 0 40px;
      display: grid;
      align-content: center;
      gap: 18px;
    }
    .topbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      color: #39516e;
      font-size: 13px;
    }
    .mark {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      font-weight: 800;
      color: var(--ink);
    }
    .mark::before {
      content: "";
      width: 34px;
      height: 34px;
      border-radius: 10px;
      background: linear-gradient(135deg, #1258b8, #00a083);
      box-shadow: 0 12px 24px rgba(18, 88, 184, .22);
    }
    .hero {
      display: grid;
      grid-template-columns: minmax(0, 1.04fr) minmax(360px, .68fr);
      gap: 18px;
      align-items: stretch;
    }
    .intro, .login, .portal {
      border: 1px solid rgba(179, 197, 218, .8);
      border-radius: 20px;
      background: var(--panel);
      box-shadow: var(--shadow);
      backdrop-filter: blur(16px);
    }
    .intro {
      padding: 34px;
      overflow: hidden;
      position: relative;
    }
    .intro::after {
      content: "";
      position: absolute;
      right: -70px;
      bottom: -110px;
      width: 310px;
      height: 310px;
      border-radius: 50%;
      border: 42px solid rgba(18, 88, 184, .08);
    }
    .kicker {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 7px 10px;
      border: 1px solid #cddced;
      border-radius: 999px;
      background: #f7fbff;
      color: #1f5c9d;
      font-size: 13px;
      font-weight: 800;
    }
    .kicker::before {
      content: "";
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: #00a083;
      box-shadow: 0 0 0 5px rgba(0, 160, 131, .13);
    }
    h1 {
      margin: 18px 0 12px;
      max-width: 680px;
      font-size: clamp(34px, 5vw, 58px);
      line-height: 1.03;
      letter-spacing: 0;
    }
    .lead {
      max-width: 660px;
      margin: 0;
      color: var(--muted);
      font-size: 16px;
      line-height: 1.85;
    }
    .meta-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 28px;
      max-width: 700px;
    }
    .meta {
      padding: 16px;
      border: 1px solid #dbe6f2;
      border-radius: 14px;
      background: rgba(248, 251, 255, .78);
    }
    .meta b {
      display: block;
      margin-bottom: 5px;
      font-size: 18px;
    }
    .meta span {
      color: #667b94;
      font-size: 12px;
    }
    .login {
      padding: 28px;
      display: grid;
      align-content: center;
    }
    .login h2, .portal h2 {
      margin: 0 0 8px;
      font-size: 24px;
      letter-spacing: 0;
    }
    .login p, .portal p {
      margin: 0 0 22px;
      color: var(--muted);
      line-height: 1.7;
      font-size: 14px;
    }
    label {
      display: block;
      margin-bottom: 8px;
      color: #27415f;
      font-weight: 800;
      font-size: 14px;
    }
    .password-row {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 10px;
    }
    input {
      width: 100%;
      height: 48px;
      border: 1px solid #bfd0e2;
      border-radius: 12px;
      padding: 0 14px;
      font-size: 18px;
      outline: none;
      background: #fff;
      color: var(--ink);
    }
    input:focus {
      border-color: var(--brand);
      box-shadow: 0 0 0 4px rgba(18, 88, 184, .12);
    }
    button, .open-btn {
      border: 0;
      border-radius: 12px;
      background: #0d5ec4;
      color: #fff;
      font-size: 15px;
      font-weight: 900;
      cursor: pointer;
      text-decoration: none;
    }
    button {
      height: 48px;
      padding: 0 20px;
      white-space: nowrap;
    }
    button:disabled {
      cursor: wait;
      opacity: .68;
    }
    .status {
      min-height: 22px;
      margin-top: 14px;
      color: var(--danger);
      font-size: 13px;
      line-height: 1.6;
    }
    .hint {
      margin-top: 18px;
      color: #7a8da5;
      font-size: 12px;
      line-height: 1.65;
    }
    .portal {
      display: none;
      padding: 28px;
    }
    .portal.active { display: block; }
    .cards {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
    }
    .card {
      min-height: 230px;
      padding: 22px;
      border: 1px solid #d5e2ef;
      border-radius: 18px;
      background:
        linear-gradient(180deg, rgba(255,255,255,.88), rgba(246,250,255,.92)),
        linear-gradient(135deg, rgba(18,88,184,.12), rgba(0,134,111,.08));
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      box-shadow: 0 12px 30px rgba(8, 31, 61, .08);
    }
    .card small {
      display: inline-flex;
      width: fit-content;
      padding: 6px 9px;
      border-radius: 999px;
      background: #e9f2ff;
      color: #155ba5;
      font-weight: 900;
      font-size: 12px;
    }
    .card h3 {
      margin: 14px 0 10px;
      font-size: 25px;
      line-height: 1.2;
    }
    .card p {
      margin: 0;
      min-height: 48px;
      color: #5e728a;
      line-height: 1.7;
      font-size: 14px;
    }
    .chips {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin: 18px 0 20px;
    }
    .chip {
      padding: 6px 8px;
      border-radius: 8px;
      background: #f0f5fb;
      color: #435b76;
      font-size: 12px;
      font-weight: 700;
    }
    .open-btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      height: 44px;
      padding: 0 16px;
      background: #09213f;
    }
    .open-btn.secondary {
      background: #0f7665;
    }
    .secure-note {
      display: flex;
      gap: 10px;
      align-items: flex-start;
      margin-top: 18px;
      padding: 14px;
      border-radius: 14px;
      background: #f2f7fc;
      color: #51677f;
      font-size: 13px;
      line-height: 1.65;
    }
    .secure-note b { color: var(--ink); }
    @media (max-width: 900px) {
      .hero, .cards { grid-template-columns: 1fr; }
      .meta-grid { grid-template-columns: 1fr; }
      .page { align-content: start; padding-top: 22px; }
    }
    @media (max-width: 560px) {
      .password-row { grid-template-columns: 1fr; }
      button { width: 100%; }
      .intro, .login, .portal { padding: 22px; border-radius: 16px; }
      h1 { font-size: 34px; }
    }
  </style>
</head>
<body>
  <main class="page">
    <div class="topbar">
      <div class="mark">PFS销售数据分析平台</div>
      <div>GitHub Pages · 本地解密 · 加密发布</div>
    </div>

    <section class="hero" id="lockedView">
      <div class="intro">
        <span class="kicker">经营分析入口</span>
        <h1>PFS销售数据分析平台</h1>
        <div class="meta-grid">
          <div class="meta"><b>2</b><span>份核心看板</span></div>
          <div class="meta"><b>AES-GCM</b><span>浏览器本地解密</span></div>
          <div class="meta"><b>2026 · 1-5月</b><span>当前分析周期</span></div>
        </div>
      </div>

      <div class="login">
        <h2>访问验证</h2>
        <p>输入访问密码后进入看板门户。密码不会发送到服务器。</p>
        <label for="password">访问密码</label>
        <div class="password-row">
          <input id="password" type="password" autocomplete="current-password" autofocus>
          <button id="unlock">解锁门户</button>
        </div>
        <div id="status" class="status"></div>
        <div class="secure-note">
          <span>●</span>
          <div><b>安全说明：</b>GitHub Pages 只托管加密后的内容；解密在本机浏览器完成。请勿把密码发到公开群聊。</div>
        </div>
        <div class="hint">推荐使用最新版 Chrome 或 Edge。首次解密大文件可能需要数秒。</div>
      </div>
    </section>

    <section class="portal" id="portalView">
      <h2>选择看板</h2>
      <p>已解锁。请选择要查看的分析页面，打开时会继续在当前浏览器内解密。</p>
      <div class="cards" id="cards"></div>
    </section>
  </main>

  <script>
    const PORTAL = ${JSON.stringify(payload)};
    const textEncoder = new TextEncoder();
    const statusEl = document.getElementById("status");
    const passwordEl = document.getElementById("password");
    const unlockEl = document.getElementById("unlock");
    const lockedView = document.getElementById("lockedView");
    const portalView = document.getElementById("portalView");
    const cardsEl = document.getElementById("cards");

    let unlockedPassword = sessionStorage.getItem("tbfx-dashboard-password") || "";

    function fromBase64(value) {
      const binary = atob(value);
      const bytes = new Uint8Array(binary.length);
      for (let i = 0; i < binary.length; i += 1) bytes[i] = binary.charCodeAt(i);
      return bytes;
    }

    async function deriveKey(password, page) {
      const material = await crypto.subtle.importKey(
        "raw",
        textEncoder.encode(password),
        "PBKDF2",
        false,
        ["deriveKey"]
      );
      return crypto.subtle.deriveKey(
        {
          name: "PBKDF2",
          hash: "SHA-256",
          salt: fromBase64(page.encrypted.salt),
          iterations: page.encrypted.iterations,
        },
        material,
        { name: "AES-GCM", length: 256 },
        false,
        ["decrypt"]
      );
    }

    async function gunzip(bytes) {
      if (!("DecompressionStream" in window)) {
        throw new Error("当前浏览器不支持本地解压，请使用最新版 Chrome 或 Edge。");
      }
      const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream("gzip"));
      return new Uint8Array(await new Response(stream).arrayBuffer());
    }

    async function decryptPage(password, page) {
      const key = await deriveKey(password, page);
      const ciphertext = fromBase64(page.encrypted.data);
      const tag = fromBase64(page.encrypted.tag);
      const packed = new Uint8Array(ciphertext.length + tag.length);
      packed.set(ciphertext);
      packed.set(tag, ciphertext.length);
      const decrypted = await crypto.subtle.decrypt(
        { name: "AES-GCM", iv: fromBase64(page.encrypted.iv), tagLength: 128 },
        key,
        packed
      );
      const htmlBytes = await gunzip(new Uint8Array(decrypted));
      return new TextDecoder("utf-8").decode(htmlBytes);
    }

    function pageById(id) {
      return PORTAL.pages.find((page) => page.id === id) || PORTAL.pages[0];
    }

    function showPortal() {
      lockedView.style.display = "none";
      portalView.classList.add("active");
      cardsEl.innerHTML = PORTAL.pages.map((page, index) => {
        const cls = index === 0 ? "open-btn" : "open-btn secondary";
        return '<article class="card">' +
          '<div>' + (page.eyebrow ? '<small>' + escapeHtml(page.eyebrow) + '</small>' : '') +
          '<h3>' + escapeHtml(page.title) + '</h3>' +
          '<p>' + escapeHtml(page.subtitle) + '</p></div>' +
          '<a class="' + cls + '" href="' + page.href + '" data-open="' + page.id + '">打开看板</a>' +
        '</article>';
      }).join("");
      document.querySelectorAll("[data-open]").forEach((link) => {
        link.addEventListener("click", async (event) => {
          event.preventDefault();
          await openDashboard(link.dataset.open);
        });
      });
    }

    async function unlockPortal() {
      const password = passwordEl.value || unlockedPassword;
      if (!password) {
        statusEl.textContent = "请输入访问密码。";
        return;
      }
      unlockEl.disabled = true;
      statusEl.textContent = "正在验证密码...";
      try {
        await decryptPage(password, pageById(PORTAL.defaultRoute));
        unlockedPassword = password;
        sessionStorage.setItem("tbfx-dashboard-password", password);
        statusEl.textContent = "";
        showPortal();
      } catch (error) {
        sessionStorage.removeItem("tbfx-dashboard-password");
        statusEl.textContent = "密码不正确，或浏览器不支持该加密页面。";
        unlockEl.disabled = false;
      }
    }

    async function openDashboard(id) {
      const page = pageById(id);
      statusEl.textContent = "";
      try {
        const html = await decryptPage(unlockedPassword, page);
        document.open();
        document.write(html);
        document.close();
      } catch (error) {
        sessionStorage.removeItem("tbfx-dashboard-password");
        unlockedPassword = "";
        portalView.classList.remove("active");
        lockedView.style.display = "";
        unlockEl.disabled = false;
        statusEl.textContent = "解密失败，请重新输入密码。";
      }
    }

    function escapeHtml(value) {
      return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
    }

    unlockEl.addEventListener("click", unlockPortal);
    passwordEl.addEventListener("keydown", (event) => {
      if (event.key === "Enter") unlockPortal();
    });

    if (unlockedPassword) {
      passwordEl.value = unlockedPassword;
      unlockPortal();
    }
  </script>
</body>
</html>`;
}
