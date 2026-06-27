#!/usr/bin/env python3
"""
build-injector.py — regenerate data-injector.html from the current dashboard.

The injector is a standalone local tool: drop a weekly .xlsx/.csv into it and it
produces a ready-to-deploy index.html with the data baked in. It works by
embedding the *current* retail_dashboard.html (base64) as a template, so this
script must be re-run whenever the dashboard changes.

Usage:  python3 build-injector.py
"""
import base64
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
DASH = ROOT / "retail_dashboard.html"
OUT = ROOT / "data-injector.html"

PLACEHOLDER = '<script id="bakedData" type="application/json">null</script>'

if not DASH.exists():
    sys.exit(f"ERROR: {DASH} not found")

html = DASH.read_text(encoding="utf-8")
if PLACEHOLDER not in html:
    sys.exit(
        "ERROR: dashboard is missing the bakedData slot:\n"
        f"  {PLACEHOLDER}\n"
        "Add it back before building the injector."
    )

b64 = base64.b64encode(html.encode("utf-8")).decode("ascii")

INJECTOR_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Dashboard 数据注入工具 · Data Injector</title>
<script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
<style>
  :root{
    --bg:#f5f5f7; --surface:#fff; --ink:#1d1d1f; --ink-2:#333; --muted:#7a7a7a;
    --primary:#0066cc; --hairline:#e0e0e0; --pos:#0066cc; --neg:#e84444;
    --ok-bg:rgba(0,102,204,.08); --warn-bg:rgba(232,68,68,.08);
  }
  *{box-sizing:border-box;}
  body{
    margin:0; background:var(--bg); color:var(--ink);
    font-family:"SF Pro Display","SF Pro Text",-apple-system,BlinkMacSystemFont,"Inter","Segoe UI",sans-serif;
    -webkit-font-smoothing:antialiased; padding:40px 20px; line-height:1.5;
  }
  .wrap{max-width:680px; margin:0 auto;}
  h1{font-size:28px; font-weight:600; letter-spacing:-.022em; margin:0 0 6px;}
  .sub{font-size:15px; color:var(--muted); margin:0 0 28px;}
  .card{background:var(--surface); border:1px solid var(--hairline); border-radius:18px; padding:26px 28px; margin-bottom:18px;}
  .step-eyebrow{font-size:12px; font-weight:600; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); margin-bottom:10px;}
  .drop{
    border:2px dashed var(--hairline); border-radius:14px; padding:38px 20px; text-align:center;
    cursor:pointer; transition:border-color .2s, background .2s;
  }
  .drop:hover, .drop.over{border-color:var(--primary); background:var(--ok-bg);}
  .drop-title{font-size:17px; font-weight:600; margin-bottom:4px;}
  .drop-hint{font-size:13px; color:var(--muted);}
  input[type=file]{display:none;}
  .result{display:none;}
  .result.show{display:block;}
  .stat-row{display:flex; flex-wrap:wrap; gap:18px; margin:14px 0 20px;}
  .stat{flex:1; min-width:120px;}
  .stat-val{font-size:24px; font-weight:600; letter-spacing:-.018em; font-variant-numeric:tabular-nums;}
  .stat-lbl{font-size:11px; font-weight:600; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); margin-top:2px;}
  .btn{
    display:inline-flex; align-items:center; gap:8px; border:none; border-radius:9999px;
    background:var(--primary); color:var(--surface); font-size:15px; font-weight:600;
    padding:12px 26px; cursor:pointer; transition:transform .1s, opacity .2s; text-decoration:none;
  }
  .btn:active{transform:scale(.96);}
  .btn.ghost{background:transparent; color:var(--primary); border:1px solid var(--hairline);}
  .msg{font-size:13px; padding:12px 14px; border-radius:10px; margin-top:14px;}
  .msg.warn{background:var(--warn-bg); color:var(--neg);}
  .msg.ok{background:var(--ok-bg); color:var(--primary);}
  ol.flow{margin:0; padding-left:20px; font-size:14px; color:var(--ink-2);}
  ol.flow li{margin:6px 0;}
  code{background:var(--bg); border:1px solid var(--hairline); border-radius:6px; padding:1px 6px; font-size:12.5px;}
  .footer{font-size:12px; color:var(--muted); text-align:center; margin-top:24px;}
</style>
</head>
<body>
<div class="wrap">
  <h1>Dashboard 数据注入工具</h1>
  <p class="sub">Data Injector · 把每周数据烤进看板，生成可直接部署的文件</p>

  <div class="card">
    <div class="step-eyebrow">Step 1 · 选择本周数据</div>
    <div id="drop" class="drop">
      <div class="drop-title">拖入 .xlsx / .csv，或点击选择</div>
      <div class="drop-hint">Drop or click to choose your weekly sales file · 全程在本机完成，数据不上传</div>
    </div>
    <input id="file" type="file" accept=".xlsx,.xls,.csv" />
    <div id="msg"></div>
  </div>

  <div id="result" class="card result">
    <div class="step-eyebrow">Step 2 · 下载并部署</div>
    <div class="stat-row">
      <div class="stat"><div id="statRows" class="stat-val">—</div><div class="stat-lbl">Rows · 数据行</div></div>
      <div class="stat"><div id="statStores" class="stat-val">—</div><div class="stat-lbl">Stores · 门店</div></div>
      <div class="stat"><div id="statRange" class="stat-val" style="font-size:15px">—</div><div class="stat-lbl">Date Range · 日期范围</div></div>
    </div>
    <button id="download" class="btn">下载 index.html · Download</button>
    <div id="msg2" class="msg ok" style="display:none"></div>
    <ol class="flow" style="margin-top:18px">
      <li>下载得到 <code>index.html</code>（已含本周数据）</li>
      <li>打开 Vercel，把这个 <code>index.html</code> 拖上去重新部署</li>
      <li>同事打开 <code>miniso-neon.vercel.app</code> 即看到本周数据，无需任何操作</li>
    </ol>
  </div>

  <p class="footer">Built from dashboard template · __BUILD_TAG__</p>
</div>

<script>
/* The current dashboard, base64-encoded, with a bakedData slot to fill. */
const DASH_B64 = "__DASH_B64__";
const BAKED_PLACEHOLDER = '<script id="bakedData" type="application/json">null<\/script>';

function b64ToUtf8(b64){
  const bin = atob(b64);
  const bytes = new Uint8Array(bin.length);
  for (let i=0;i<bin.length;i++) bytes[i] = bin.charCodeAt(i);
  return new TextDecoder('utf-8').decode(bytes);
}

const STORE_KEYS = ['Store','店铺名称','门店名称','店铺','门店','Store Name'];
const DATE_KEYS  = ['Date','日历日期','日期','Day'];

let bakedHtml = null;

const drop = document.getElementById('drop');
const fileInput = document.getElementById('file');
const msg = document.getElementById('msg');
const result = document.getElementById('result');

drop.addEventListener('click', () => fileInput.click());
['dragover','dragenter'].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.add('over'); }));
['dragleave','drop'].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.remove('over'); }));
drop.addEventListener('drop', e => { const f = e.dataTransfer.files[0]; if (f) handle(f); });
fileInput.addEventListener('change', e => { const f = e.target.files[0]; if (f) handle(f); });

function showMsg(text, kind){ msg.className = 'msg ' + kind; msg.textContent = text; }

function firstKey(row, keys){ for (const k of keys) if (k in row) return k; return null; }

function handle(file){
  showMsg('Reading · 解析中…', 'ok');
  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const data = new Uint8Array(e.target.result);
      const wb = XLSX.read(data, { type:'array', cellDates:false });   // same options as the dashboard
      const sheet = wb.Sheets[wb.SheetNames[0]];
      const rows = XLSX.utils.sheet_to_json(sheet, { defval:null });
      if (!rows.length){ showMsg('文件为空 · No rows found', 'warn'); return; }

      const sample = rows[0];
      const storeKey = firstKey(sample, STORE_KEYS);
      const dateKey  = firstKey(sample, DATE_KEYS);
      if (!storeKey || !dateKey){
        showMsg('未找到 门店 或 日期 列，请确认表头与看板一致 · Missing Store/Date column', 'warn');
        return;
      }

      // Bake: raw sheet rows go straight into the dashboard's own ingestRows().
      const payload = { fileName: file.name, timestamp: Date.now(), rows };
      const json = JSON.stringify(payload).replace(/</g, '\\u003c');
      const tpl = b64ToUtf8(DASH_B64);
      bakedHtml = tpl.replace(BAKED_PLACEHOLDER,
        '<script id="bakedData" type="application/json">' + json + '<\/script>');

      // Summary stats
      const stores = new Set(rows.map(r => r[storeKey]).filter(Boolean));
      const serials = rows.map(r => r[dateKey]).filter(v => typeof v === 'number');
      let range = '—';
      if (serials.length){
        const toDate = (n) => { const o = XLSX.SSF.parse_date_code(n); return o ? `${o.y}-${String(o.m).padStart(2,'0')}-${String(o.d).padStart(2,'0')}` : '?'; };
        range = `${toDate(Math.min(...serials))} → ${toDate(Math.max(...serials))}`;
      }
      document.getElementById('statRows').textContent   = rows.length.toLocaleString();
      document.getElementById('statStores').textContent = stores.size.toLocaleString();
      document.getElementById('statRange').textContent  = range;

      showMsg('✓ 解析成功 · Parsed successfully', 'ok');
      result.classList.add('show');
      result.scrollIntoView({ behavior:'smooth', block:'nearest' });
    } catch (err) {
      showMsg('解析失败 · Parse error: ' + err.message, 'warn');
    }
  };
  reader.readAsArrayBuffer(file);
}

document.getElementById('download').addEventListener('click', () => {
  if (!bakedHtml) return;
  const blob = new Blob([bakedHtml], { type:'text/html' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'index.html';
  document.body.appendChild(a); a.click(); a.remove();
  URL.revokeObjectURL(url);
  const m = document.getElementById('msg2');
  m.style.display = 'block';
  m.textContent = '✓ 已下载 index.html — 现在把它拖到 Vercel 重新部署即可。';
});
</script>
</body>
</html>
"""

build_tag = f"{DASH.name} · {len(html):,} chars"
out = (INJECTOR_TEMPLATE
       .replace("__DASH_B64__", b64)
       .replace("__BUILD_TAG__", build_tag))
OUT.write_text(out, encoding="utf-8")
print(f"OK  wrote {OUT.name}  ({len(out):,} bytes, template {len(html):,} chars)")
