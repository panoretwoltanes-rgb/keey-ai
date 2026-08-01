# KEEY_AI_Quote 项目清理计划

> 本文件只做清理规划，不执行删除。确认后另行操作。

## 一、当前目录结构

```
KEEY_AI_Quote/
├── app.py                  Flask 入口
├── config.py               配置
├── requirements.txt        依赖
├── start.bat               启动脚本（Flask + Tunnel）
├── 一键启动.bat             备用启动脚本
├── build_series_mapping.py 系列映射生成工具
├── read_accessory_param.py 临时诊断脚本
├── read_wb06055.py         临时诊断脚本
├── validate_accessory_regex.py 临时验证脚本
├── test_*.py               (13 个) 开发测试脚本
├── cleanup_plan.md         本文件
├── data/                   配置/数据 JSON
├── deploy/                 部署辅助
├── logs/                   空目录
├── output/                 Excel 输出 + SQLite
├── parser/                 空目录
├── quote/                  空目录
├── routes/                 Flask 路由
├── services/               业务服务层
├── static/                 前端静态资源
├── temp/                   空目录
├── templates/              HTML 模板
├── uploads/                空目录
└── __pycache__/            Python 缓存
```

## 二、文件状态

### 【保留】核心运行文件

| 文件 | 原因 |
|------|------|
| `app.py` | Flask 入口，必须保留 |
| `config.py` | 项目配置 |
| `requirements.txt` | 依赖清单 |
| `start.bat` | 一键启动（Flask + Tunnel） |
| `routes/quote.py` | API 路由 |
| `routes/__init__.py` | 路由包 |
| `services/__init__.py` | 服务包 |
| `services/parser_service.py` | 报价解析 |
| `services/quote_service.py` | 报价业务 |
| `services/excel_service.py` | Excel 生成 |
| `services/history_service.py` | 历史记录 |
| `services/api_service.py` | API 服务层 |
| `services/database_service.py` | SQLite 数据库 |
| `services/product_service.py` | 产品查询 |
| `services/product_lookup_service.py` | 精确查库 |
| `services/product_text_parser.py` | NLP 产品解析 |
| `services/accessory_service.py` | 配件匹配 |
| `services/product_database_search_service.py` | 产品库搜索 |
| `services/product_matcher_service.py` | 产品匹配 |
| `services/quote_schema.py` | 数据模型 |
| `services/pricing_service.py` | 价格计算 |
| `services/discount_service.py` | 折扣计算 |
| `services/ai_parser_service.py` | AI 解析层 |
| `services/ai_order_schema.py` | AI 订单结构 |
| `services/order_builder_service.py` | 订单构建 |
| `services/product_category_service.py` | 分类服务 |
| `templates/index.html` | 首页模板 |
| `static/app.js` | 前端逻辑 |
| `static/style.css` | 前端样式 |
| `output/quote.db` | SQLite 数据库（历史报价） |
| `data/products.json` | 产品数据（保留但不作为报价源） |
| `data/product_series.json` | 系列映射配置 |
| `data/product_alias.json` | 产品别名 |
| `data/product_keyword_rules.json` | 关键词规则 |
| `data/product_category_map.json` | 分类映射 |
| `data/accessory_directives.json` | 配件指令 |
| `data/accessory_mapping.json` | 配件映射 |

### 【待确认】可能保留的工具/辅助

| 文件 | 原因 |
|------|------|
| `build_series_mapping.py` | 产品库映射维护工具（非运行必需，但以后可用） |
| `deploy/start_server.bat` | 部署辅助（单独启动 Flask） |
| `deploy/start_tunnel.bat` | 部署辅助（单独启动 Tunnel） |
| `deploy/README.md` | 部署说明 |
| `一键启动.bat` | 与 `start.bat` 功能重复，二选一 |
| `output/*.xlsx` (10 个) | 历史报价文件，是否清理由你决定 |
| `logs/` / `temp/` / `uploads/` | 空目录，可保留也可删除 |

### 【删除】开发过程遗留文件

| 文件 | 原因 |
|------|------|
| `read_accessory_param.py` | 临时数据库诊断脚本，已完成使命 |
| `read_wb06055.py` | 临时产品库读取脚本，已完成使命 |
| `validate_accessory_regex.py` | 临时正则验证脚本，已完成使命 |
| `test_accessory_flow.py` | 开发测试脚本，不属于运行版本 |
| `test_ai_parser.py` | 开发测试脚本 |
| `test_ai_quote_flow.py` | 开发测试脚本 |
| `test_category_match.py` | 开发测试脚本 |
| `test_database_score.py` | 开发测试脚本 |
| `test_order_builder.py` | 开发测试脚本 |
| `test_product_alias.py` | 开发测试脚本 |
| `test_product_database_scan.py` | 开发测试脚本 |
| `test_product_matcher.py` | 开发测试脚本 |
| `test_product_parser.py` | 开发测试脚本 |
| `test_quote_flow_8_scenarios.py` | 8 场景验证脚本 |
| `test_real_customer_cases.py` | 客户案例测试脚本 |
| `parser/` | 空目录（旧结构残留） |
| `quote/` | 空目录（旧结构残留） |
| `__pycache__/` | Python 缓存 |
| `services/__pycache__/` | Python 缓存 |
| `routes/__pycache__/` | Python 缓存 |

## 三、删除计划

### 明确删除（16 项）

1. `read_accessory_param.py` — 临时诊断，已完成
2. `read_wb06055.py` — 临时诊断，已完成
3. `validate_accessory_regex.py` — 临时验证，已完成
4. `test_accessory_flow.py` — 测试脚本，不参与运行
5. `test_ai_parser.py` — 测试脚本
6. `test_ai_quote_flow.py` — 测试脚本
7. `test_category_match.py` — 测试脚本
8. `test_database_score.py` — 测试脚本
9. `test_order_builder.py` — 测试脚本
10. `test_product_alias.py` — 测试脚本
11. `test_product_database_scan.py` — 测试脚本
12. `test_product_matcher.py` — 测试脚本
13. `test_product_parser.py` — 测试脚本
14. `test_quote_flow_8_scenarios.py` — 测试脚本
15. `test_real_customer_cases.py` — 测试脚本
16. `parser/` — 空目录
17. `quote/` — 空目录
18. `__pycache__/` — Python 缓存
19. `services/__pycache__/` — Python 缓存
20. `routes/__pycache__/` — Python 缓存

### 建议删除（待你确认）

1. `一键启动.bat` — 与 `start.bat` 功能重复
2. `logs/` — 空目录
3. `temp/` — 空目录
4. `uploads/` — 空目录
5. `output/` 中的历史 xlsx — 按需保留最近记录

### 保留（不建议动）

1. `build_series_mapping.py` — 产品库维护工具
2. `deploy/` — 部署辅助脚本
3. `data/` 全部配置 — 运行必需
4. `output/quote.db` — 历史报价数据库
5. `services/` 全部业务模块 — 运行必需

## 四、确认方式

回复「确认删除」即执行明确删除项；
回复「确认全部」则同时删除建议删除项。
