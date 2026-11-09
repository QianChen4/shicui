# 拾萃开发说明

- 用户用中文沟通。只做 Mac + Chrome，不支持 Safari，不做 Windows，不做桌面窗口版。
- 整个程序是单文件 `拾萃.html`（数据存在用户选的文件夹里，用 File System Access API）。可以加 `?demo` 用演示数据测试。

## 版本号

- `拾萃.html` 里有两个版本：`APP_VERSION` 是数据格式版本，改了数据结构才加；`PROGRAM_VERSION` 是程序版本。
- 程序版本：v1.x 是加入在线更新以前，v2.x 起有在线更新。重大更新改第一位，小功能改中间一位，极小改动只改最后一位。
- 不要删 `拾萃.html` 里“兼容旧版更新：const PROGRAM_VERSION='…'”注释，也不要删 latest.json 的 `version` 字段：v2.6.0 以前的更新程序只认第一位加 1 的旧编号（3.x）。这两处由 `tools/release.py` 自动维护。

## 发布（合并到 main 就是发布）

每次改动 `拾萃.html`：
1. 改 `PROGRAM_VERSION`。
2. 在 `更新记录.md` 最上面加 `## v版本号（日期）` 一节，逐条写更新内容（会显示给用户）。
3. 运行 `python3 tools/release.py`，生成 latest.json（CI 会用 `--check` 检查是否一致）。
4. 顺带更新 `README.md` 的使用说明，写给第一次下载的人。在线更新只替换 `拾萃.html`，不会改用户本地的说明。

在线更新读取 `https://raw.githubusercontent.com/QianChen4/shicui/main/latest.json`，连不上时用 jsDelivr 和几个国内加速地址（要求两个来源一致），下载后校验 sha256。仓库地址变了要同时改 `UPDATE_RAW` 和 jsDelivr 那一行。
