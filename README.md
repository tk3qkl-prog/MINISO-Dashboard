# MINISO Retail Performance Dashboard · 零售业绩看板

单文件 HTML 零售数据看板（Apple 设计风格，中英双语）。门店销售 / 坪效 / ATV / UPT / YoY / 周末提升 / 多店对比 / 门店排行，支持本地 xlsx/csv 上传与 IndexedDB 缓存。

## 文件 · Files

| 文件 | 说明 |
|---|---|
| `retail_dashboard.html` | 看板本体（空白/上传版）。含 `#bakedData` 数据槽，默认空时走上传 + 本地缓存 |
| `data-injector.html` | 数据注入工具：拖入每周 xlsx → 生成已含数据的 `index.html` 部署到 Vercel |
| `build-injector.py` | 从当前 `retail_dashboard.html` 重新生成注入工具 |
| `使用说明-数据更新.md` | 每周数据更新流程（给非技术使用者） |

## 更新代码后 · After editing the dashboard

改动 `retail_dashboard.html` 后，重新生成注入工具：

```bash
python3 build-injector.py
```

## 「一人上传，所有人看」工作流

1. 双击 `data-injector.html`，拖入本周 xlsx → 下载 `index.html`
2. 把 `index.html` 部署到 Vercel
3. 同事打开站点即看最新数据，无需任何操作

注入工具把原始表格行烤进看板，看板用同一个 `ingestRows()` 处理 —— 与手动上传结果完全一致。

## 部署 · Deploy

当前部署：[miniso-neon.vercel.app](https://miniso-neon.vercel.app)
