# 杭州到青岛亲子自驾路书

3 天 2 晚亲子自驾路书的静态网页项目。`index.html` 初始内容与用户提供的 HTML 文件一致。

## 项目结构

- `index.html`：网页入口及路书内容。
- `.nojekyll`：让 GitHub Pages 直接发布静态文件。
- `.gitignore`：忽略 macOS 的 `.DS_Store` 文件。
- `README.md`：项目说明及更新方法。

## 发布方式

公开仓库：[timothylkelly-del/hangzhou-qingdao-trip](https://github.com/timothylkelly-del/hangzhou-qingdao-trip)。

网页地址（Pages 部署完成后生效）：[杭州到青岛亲子自驾路书](https://timothylkelly-del.github.io/hangzhou-qingdao-trip/)。

在仓库的 **Settings → Pages** 中选择 **Deploy from a branch**，发布来源为 **main** 分支的 **/(root)** 目录。实际部署状态以 GitHub Pages 设置页及公开网址验证为准。

## 后续更新

1. 编辑 `index.html`，或用新版完整 HTML 替换该文件，保持文件名为 `index.html`。
2. 本地打开网页检查内容与排版。
3. 将修改提交并推送到远程仓库的 `main` 分支。
4. 等待 GitHub Pages 部署完成，再打开公开网址确认更新。

无需构建命令或额外依赖。后续若增加图片等文件，可放在 `assets/` 目录，并在 HTML 中使用相对路径引用。
