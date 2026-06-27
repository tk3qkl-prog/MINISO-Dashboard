# MINISO Retail Performance Dashboard · 零售业绩看板

单文件 HTML 零售数据展示工具（Apple 设计风格，中英双语）。使用者**自行上传** `.xlsx` / `.csv` 销售报表，在本地浏览器解析并展示，数据不上云。

门店销售 / 坪效 / ATV / UPT / YoY / 周末提升 / 多店对比 / 门店排行 / 同店类型筛选 / 日销售走势（Revenue·ATV·UPT 切换、周末标色、数据标签）。上传后数据会缓存在**本机浏览器**（IndexedDB），下次打开免重传；换数据直接重新上传即可。

## 文件 · Files

| 文件 | 说明 |
|---|---|
| `index.html` | 看板本体，也是部署入口。全部功能在这一个文件里 |

## 部署 · Deploy（GitHub → Vercel 自动部署）

代码已连接 Vercel 自动部署。更新流程：

1. 修改 `index.html`
2. 在 **GitHub Desktop** 填写说明 → **Commit to main** → **Push origin**
3. Vercel 自动检测并重新部署，约 1 分钟后线上更新

## 数据表头要求 · Data columns

支持中英文表头（如 `日历日期`/`Date`、`销售金额本期`/`Revenue`、`店铺名称`/`Store` 等）。需包含：门店、日期、销售金额、客单量、销售数量、面积、城市、开业时间。详见 `index.html` 顶部 `FIELD_ALIASES` 注释。
