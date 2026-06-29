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
const pages = [
  {
    title: "2026年与2025年1-5月数据对比分析",
    source: "F:\\llqdocument\\大成文件\\客户贡献分析\\26年与25年_1-5月数据对比分析.html",
    output: path.join(root, "index.html"),
  },
  {
    title: "2026年1-5月数据分析仪表盘",
    source: "F:\\llqdocument\\大成文件\\客户贡献分析\\2026年1-5月数据分析仪表盘.html",
    output: path.join(root, "2026-dashboard.html"),
  },
];

function b64(buffer) {
  return Buffer.from(buffer).toString("base64");
}

function encryptFile(page) {
  const plain = fs.readFileSync(page.source);
  const compressed = zlib.gzipSync(plain, { level: 9 });
  const salt = crypto.randomBytes(16);
  const iv = crypto.randomBytes(12);
  const iterations = 310000;
  const key = crypto.pbkdf2Sync(password, salt, iterations, 32, "sha256");
  const cipher = crypto.createCipheriv("aes-256-gcm", key, iv);
  const encrypted = Buffer.concat([cipher.update(compressed), cipher.final()]);
  const tag = cipher.getAuthTag();

  const payload = {
    title: page.title,
    kdf: "PBKDF2-SHA256",
    cipher: "AES-256-GCM",
    compression: "gzip",
    iterations,
    salt: b64(salt),
    iv: b64(iv),
    tag: b64(tag),
    data: b64(encrypted),
  };

  fs.writeFileSync(page.output, buildShell(page.title, payload), "utf8");
  console.log(`${page.output} <= encrypted ${plain.length} bytes, gzip ${compressed.length} bytes`);
}

function buildShell(title, payload) {
  return `<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${escapeHtml(title)}</title>
  <style>
    :root {
      color-scheme: light;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif;
      background: #eef4fb;
      color: #0b1f38;
    }
    body {
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      background:
        radial-gradient(circle at 18% 16%, rgba(42, 111, 255, .14), transparent 28%),
        radial-gradient(circle at 84% 20%, rgba(0, 153, 118, .12), transparent 30%),
        linear-gradient(135deg, #f7fbff 0%, #eaf2fb 100%);
    }
    .box {
      width: min(460px, calc(100vw - 40px));
      padding: 34px;
      border: 1px solid #d6e2ef;
      border-radius: 18px;
      background: rgba(255, 255, 255, .88);
      box-shadow: 0 20px 60px rgba(15, 42, 77, .14);
      backdrop-filter: blur(14px);
    }
    h1 {
      margin: 0 0 8px;
      font-size: 24px;
      letter-spacing: 0;
    }
    p {
      margin: 0 0 22px;
      color: #59708d;
      line-height: 1.7;
      font-size: 14px;
    }
    label {
      display: block;
      margin-bottom: 8px;
      color: #26415f;
      font-weight: 700;
      font-size: 14px;
    }
    input {
      box-sizing: border-box;
      width: 100%;
      height: 46px;
      border: 1px solid #bfd0e2;
      border-radius: 10px;
      padding: 0 13px;
      font-size: 16px;
      outline: none;
      background: #fff;
      color: #0b1f38;
    }
    input:focus {
      border-color: #2f6fed;
      box-shadow: 0 0 0 4px rgba(47, 111, 237, .12);
    }
    button {
      width: 100%;
      height: 46px;
      margin-top: 14px;
      border: 0;
      border-radius: 10px;
      background: #0b63ce;
      color: #fff;
      font-size: 16px;
      font-weight: 800;
      cursor: pointer;
    }
    button:disabled {
      cursor: wait;
      opacity: .68;
    }
    .status {
      min-height: 22px;
      margin-top: 14px;
      color: #bf352f;
      font-size: 13px;
      line-height: 1.6;
    }
    .hint {
      margin-top: 18px;
      color: #7a8da5;
      font-size: 12px;
    }
  </style>
</head>
<body>
  <main class="box">
    <h1>${escapeHtml(title)}</h1>
    <p>该看板已加密。请输入访问密码，浏览器会在本地解密后打开页面。</p>
    <label for="password">访问密码</label>
    <input id="password" type="password" autocomplete="current-password" autofocus>
    <button id="unlock">打开看板</button>
    <div id="status" class="status"></div>
    <div class="hint">提示：密码不会发送到服务器，解密只在当前浏览器中完成。</div>
  </main>
  <script>
    const PAYLOAD = ${JSON.stringify(payload)};

    const textEncoder = new TextEncoder();
    const statusEl = document.getElementById("status");
    const passwordEl = document.getElementById("password");
    const unlockEl = document.getElementById("unlock");

    function fromBase64(value) {
      const binary = atob(value);
      const bytes = new Uint8Array(binary.length);
      for (let i = 0; i < binary.length; i += 1) bytes[i] = binary.charCodeAt(i);
      return bytes;
    }

    async function deriveKey(password) {
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
          salt: fromBase64(PAYLOAD.salt),
          iterations: PAYLOAD.iterations,
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

    async function unlock() {
      const password = passwordEl.value;
      if (!password) {
        statusEl.textContent = "请输入访问密码。";
        return;
      }
      unlockEl.disabled = true;
      statusEl.textContent = "正在解密，请稍候...";
      try {
        const key = await deriveKey(password);
        const ciphertext = fromBase64(PAYLOAD.data);
        const tag = fromBase64(PAYLOAD.tag);
        const packed = new Uint8Array(ciphertext.length + tag.length);
        packed.set(ciphertext);
        packed.set(tag, ciphertext.length);
        const decrypted = await crypto.subtle.decrypt(
          { name: "AES-GCM", iv: fromBase64(PAYLOAD.iv), tagLength: 128 },
          key,
          packed
        );
        const htmlBytes = await gunzip(new Uint8Array(decrypted));
        const html = new TextDecoder("utf-8").decode(htmlBytes);
        document.open();
        document.write(html);
        document.close();
      } catch (error) {
        statusEl.textContent = "密码不正确，或浏览器不支持该加密页面。";
        unlockEl.disabled = false;
      }
    }

    unlockEl.addEventListener("click", unlock);
    passwordEl.addEventListener("keydown", (event) => {
      if (event.key === "Enter") unlock();
    });
  </script>
</body>
</html>`;
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

for (const page of pages) encryptFile(page);
