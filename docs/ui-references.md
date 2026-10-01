# 前端视觉参考（去 AI 味改版）

改版目标：去掉渐变大卡、假徽章、大圆角柔和标签等“生成感”，贴近真实产品与企业后台。

## 溯源页 `/t/{code}`

参考：

| 来源 | 采纳点 |
|------|--------|
| 服饰数字护照（Rudholm DPP / EON Digital ID） | 产品名 + 成分 + 产地/厂家 + 洗涤 + 履历的信息结构 |
| 国内质检吊牌/洗水唛 | 定义列表式字段、执行标准、检验员、批次号 |
| 微信/支付宝扫码结果页密度 | 白底、顶栏、分段、紧凑字号、少装饰 |
| Tabler / Element 表格审美 | 2px 圆角标签、灰线分隔、无光晕 |

要点：

- 无渐变 hero、无蜡封印章、无 timeline 发光点
- 字段用表格/定义列表，像“档案”而不是营销落地页
- 强调色仅用于状态与段标题（克制蓝）
- 圆角 2–4px，阴影几乎不用

## 后台 `/admin`

参考：

| 来源 | 采纳点 |
|------|--------|
| [tabler](https://github.com/tabler/tabler) / [coreui-free-bootstrap-admin-template](https://github.com/coreui/coreui-free-bootstrap-admin-template) | 侧栏 + 顶栏 + 白卡片 + 4px 圆角 |
| [vue-element-admin](https://github.com/PanJiaChen/vue-element-admin) / [soybean-admin](https://github.com/soybeanjs/soybean-admin) | 中文后台信息密度、统计卡、数据表格、状态 Tag |
| AdminLTE 企业后台 | 表头灰底、行 hover、按钮层级 |

要点：

- 深色侧栏 + 浅灰画布 + 白面板
- 统计四宫格、密集表格、表单分区
- 按钮实心主色 / 描边次要，不用圆角胶囊堆叠

## 明确不再使用

- 大面积 radial 光晕、多层 soft shadow
- “认证徽章”圆形装饰
- 薰衣草/香槟色大面积底
- 超大圆角（>16px）卡片堆叠
