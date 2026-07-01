# TBFX Docker 国内访问部署

这个方案用于替代腾讯云 COS 镜像：把当前 GitHub Pages 的加密看板放进 Nginx Docker 容器，在公司服务器、云服务器或本机上直接访问。

## 运行方式

```powershell
cd C:\Users\Lenovo\Documents\Codex\2026-05-20\files-mentioned-by-the-user-customer\TBFX-pages-work
$env:DASHBOARD_PASSWORD="1826"
.\publish_docker.ps1
```

启动后访问：

```text
http://localhost:8080/
```

如果部署在服务器上，把 `localhost` 换成服务器 IP：

```text
http://服务器IP:8080/
```

## 更新方式

1. 更新本地两个源 HTML 看板。
2. 重新运行：

```powershell
$env:DASHBOARD_PASSWORD="1826"
.\publish_docker.ps1
```

脚本会重新加密页面、重建镜像并替换正在运行的容器。

## 说明

- 服务器只托管加密后的 HTML。
- 密码仍在浏览器本地校验和解密，服务器不接收密码。
- Nginx 已开启 gzip，国内/内网访问会比 GitHub Pages 更稳定。
- GitHub Pages 地址仍可作为备用访问方式。
