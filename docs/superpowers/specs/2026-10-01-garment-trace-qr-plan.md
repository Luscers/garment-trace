# 服装二维码溯源 — 实现计划

依据：`docs/superpowers/specs/2026-10-01-garment-trace-qr-design.md`  
目标：按里程碑交付可投标演示的 MVP（方案 A）。

---

## 0. 约定

- 项目根：`D:\LearnAI\self\garment-trace`
- 分支：`master`，按里程碑提交
- 环境：Python 3.12+（FastAPI）、Node 20+（uni-app / admin）、MySQL 8
- API 统一响应：`{ code, message, data }`；`code=0` 成功

---

## M1 — 服务端数据模型与 API

**产出**：`server/` 可运行，单测通过

### 任务

1. 初始化 `server/`（FastAPI + SQLAlchemy + PyMySQL + uv）
2. 建表迁移：`factories` / `products` / `batches` / `trace_codes` / `users`
3. 实现公开接口 `GET /api/trace/{code}`（拼装溯源卡 JSON）
4. 实现 `POST /api/admin/login`（JWT）
5. 实现 `POST /api/admin/import`（xlsx 校验 + 事务批量生码）
6. 实现批次列表、码启停用、导出任务骨架
7. 单测：查询、导入校验（含重复款批拒绝）、启停用

### 验收

- [ ] `GET /api/trace/{code}` 返回结构符合规格 §7
- [ ] 导入失败整批回滚并返回行号原因
- [ ] 单测绿

---

## M2 — 工厂后台 admin/

**产出**：可登录、导入 Excel、导出二维码图

### 任务

1. `admin/` Vue 3 + Vite 脚手架
2. 登录页 + JWT 持久化
3. Excel 上传（xlsx）与错误行展示
4. 款/批次列表、启停用操作
5. 按批次导出 ZIP（PNG 码图，内容为 `https://{domain}/t/{code}`）

### 验收

- [ ] 导入 20 行样例数据成功
- [ ] 导出 ZIP 含可扫 PNG
- [ ] 停用码扫码进入兜底页（联调阶段）

---

## M3 — 消费者端 H5（client/）

**产出**：手机浏览器打开溯源页

### 任务

1. uni-app 工程 `client/`（Vue 3）
2. 页面 `pages/trace/index`：根据 `code` 调公开 API
3. 溯源卡 UI（字段见规格 §5）+ 无效码文案
4. 响应式、微信内打开可用

### 验收

- [ ] 有效码展示完整字段
- [ ] 无效码显示「未查询到溯源信息」

---

## M4 — 小程序端与真机验收

**产出**：微信小程序扫码可达

### 任务

1. uni-app 条件编译出微信小程序
2. 小程序路径 `pages/trace/index?code=` 与 H5 共用逻辑
3. 域名备案与小程序 request 合法域名配置说明
4. 真机：导出码 → 微信「扫一扫」→ 信息一致

### 验收

- [ ] 小程序码与 H5 展示字段一致
- [ ] 真机扫码 E2E 通过

---

## M5 — 投标演示包

**产出**：给服装厂客户看的材料

### 任务

1. 演示账号与 20 条样例数据
2. 截图：吊牌样例、扫码结果页、后台导入/导出
3. `docs/投标说明.md`：方案亮点、架构图、扩展路线
4. 可选：本地/服务器演示环境

### 验收

- [ ] 客户可扫码看到厂家、地址等信息
- [ ] 演示包可独立打开

---

## 技术要点备忘

| 项 | 约定 |
|----|------|
| 短码 | `secrets.token_urlsafe` 截取或自定义 base58，≥8 位，唯一索引 |
| 导入 | pandas/openpyxl 读 xlsx；`batch_no + style_no` 唯一 |
| JWT | HS256，过期时间可配置；仅 admin API 鉴权 |
| CORS | 开发期放开 admin 源；生产同域或白名单 |
| 导出码 | `segno`/`qrcode` 生成 PNG |

---

## 风险与缓解

| 风险 | 缓解 |
|------|------|
| 小程序合法域名/备案未就绪 | M3 先用 H5 演示；M4 出配置清单 |
| 客户临时加字段 | `batches.extra_json`，展示层可配置 |
| Excel 格式不齐 | 模板 + 服务端严格校验 + 错误行提示 |
