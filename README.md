# 服装二维码溯源 Demo

面向服装厂招标场景的**一物一码溯源 MVP**：吊牌二维码 → 扫码/打开链接 → 展示生产厂家、生产地址、批次、成分等基础溯源信息。

- 设计规格：`docs/superpowers/specs/2026-10-01-garment-trace-qr-design.md`
- 实现计划：`docs/superpowers/specs/2026-10-01-garment-trace-qr-plan.md`
- 视觉参考：`docs/ui-references.md`

## 功能概览

| 端 | 路径 | 说明 |
|----|------|------|
| 消费者溯源 H5 | `/t/{code}` | 扫码/打开码号，展示产品与厂家档案 |
| 工厂后台 | `/admin` | 登录、批量导入生码、启停用（演示） |
| 二维码演示墙 | `/demo` | 样例二维码，可下载/另扫 |
| 小程序风格 App | `miniapp/index.html` | 单文件演示（离线样例数据） |

## 技术栈

- **后端**：Python FastAPI + SQLite（演示；正式按规格切 MySQL）
- **前端**：静态 H5（可迁 uni-app 双端）
- **接口**：`GET /api/trace/{code}` 等，见 `server/app/main.py`

## 本地启动

```powershell
cd server
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8760
```

浏览器打开：

- 溯源页：http://127.0.0.1:8760/t/GT-A01-8F3K2M  
- 后台：http://127.0.0.1:8760/admin （`admin` / `yalan2026`）  
- 样例码：http://127.0.0.1:8760/demo  

生成演示二维码：

```powershell
python scripts/make_qr.py
```

首次启动会自动建表并写入 3 个款号样例。

## 目录结构

```text
garment-trace/
├── docs/                 # 设计、计划、UI 参考
├── server/               # FastAPI + 静态页
│   ├── app/
│   └── static/
├── miniapp/              # 单文件小程序风格演示
├── scripts/
└── README.md
```

## 手机扫码（简述）

`127.0.0.1` 仅本机可用。同 WiFi 演示需改为局域网 IP 或 `0.0.0.0` 监听并重打二维码；对外正式扫码需域名 + HTTPS（及备案）。

## License

演示用途；投产前请按客户与合规要求调整。
