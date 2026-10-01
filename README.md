# 服装二维码溯源 Demo

可扫码演示的 MVP（方案 A），对应设计规格 `docs/superpowers/specs/2026-10-01-garment-trace-qr-design.md`。

## 快速启动

```powershell
cd server
# 首次安装依赖
# python -m pip install -r requirements.txt

# 启动（默认 8760）
python -m uvicorn app.main:app --host 127.0.0.1 --port 8760
```

生成演示二维码：

```powershell
python scripts/make_qr.py
```

## 演示入口

| 地址 | 说明 |
|------|------|
| http://127.0.0.1:8760/demo | 二维码演示墙（手机可扫） |
| http://127.0.0.1:8760/t/GT-A01-8F3K2M | 溯源页（羊毛大衣） |
| http://127.0.0.1:8760/t/GT-A02-5R9W1P | 溯源页（真丝裙） |
| http://127.0.0.1:8760/t/GT-B01-7N4Q6X | 溯源页（衬衫） |
| http://127.0.0.1:8760/admin | 工厂后台（admin / yalan2026） |

## 结构

```
server/     FastAPI + SQLite（演示）/ 生产可换 MySQL
  static/   溯源 H5、后台、演示页、二维码 PNG
scripts/    make_qr.py
admin/      预留（当前静态页在 server/static/admin.html）
client/     预留 uni-app 双端正式工程
docs/       设计与计划
```

## 演示数据

- 工厂：宁波雅澜服饰有限公司（品牌：雅澜 YALAN）
- 3 个款号 / 批次 / 溯源码
- 后台可 JSON 批量导入并自动生码

## 与正式版差异

| Demo | 正式版（按规格） |
|------|------------------|
| SQLite | MySQL |
| 静态 H5 | uni-app 输出 H5 + 微信小程序 |
| JSON 导入 | Excel 模板导入 |
| 本机 127.0.0.1 | 备案域名 + HTTPS |
