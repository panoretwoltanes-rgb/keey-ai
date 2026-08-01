# KEEY_AI_Quote V1.0

KEEY AI 智能报价系统 - 基于自然语言输入的灯具报价 Excel 自动生成系统。

## 一、项目介绍

KEEY_AI_Quote 是面向灯具销售场景的报价工具：

- 用户输入自然语言需求（客户、项目、产品系列、开孔、色温、数量、安装方式等）
- 系统自动解析需求
- 从正式产品库（企一产品报价表）匹配产品
- 自动调用 V1 正式 Excel 报价引擎生成带图片、公式、红字的报价单
- 网页端可下载 Excel，历史报价自动归档

已验证功能：

- Flask 正常启动
- 本地访问 `http://127.0.0.1:5000`
- 局域网访问
- Cloudflare Tunnel 公网访问
- 前端页面正常
- API 正常
- 正式模板 / 产品图片 / 金额公式 / 合计 / 红字正常

## 二、技术架构

```
用户输入（网页/微信粘贴）
    ↓
NLP 解析（product_text_parser）
    ↓
系列/开孔/色温/安装方式 → 最终型号
    ↓
精确查库（product_lookup_service.exact_db_lookup）
    ↓
配件匹配（accessory_service）
    ↓
报价订单（quote_service）
    ↓
V1 正式 Excel 引擎（template_handler / image_handler / rich_text_handler）
    ↓
Excel 报价单
```

核心设计原则：

- **产品库是唯一数据源**（企一产品报价表 xlsx）
- **精确查库替代模糊搜索**：NLP 得到最终型号后直接读取唯一数据库记录
- **V1 Excel 引擎不修改**：模板、图片、公式、红字全部沿用 V1 已验证逻辑

## 三、目录结构说明

```
KEEY_AI_Quote/
├── app.py                     Flask 入口（host=0.0.0.0, port=5000）
├── config.py                  配置（端口、目录、密钥）
├── requirements.txt           依赖清单
├── start.bat                  一键启动（Flask + Cloudflare Tunnel）
├── 一键启动.bat               备用一键启动脚本
├── build_series_mapping.py    产品库系列映射生成工具
├── routes/
│   └── quote.py               页面/API/下载/历史 路由
├── services/
│   ├── api_service.py         API 统一入口
│   ├── quote_service.py       报价业务编排
│   ├── parser_service.py      旧格式解析（回退）
│   ├── product_text_parser.py NLP 产品文本解析
│   ├── product_lookup_service.py 精确查库（唯一入口）
│   ├── product_database_search_service.py 产品库评分搜索（辅助）
│   ├── product_matcher_service.py 产品匹配
│   ├── product_service.py     产品查询
│   ├── accessory_service.py   配件（预埋盒）匹配
│   ├── excel_service.py       Excel 生成（调用 V1 模板函数）
│   ├── database_service.py    SQLite 历史记录
│   ├── history_service.py     历史记录管理
│   ├── pricing_service.py     金额计算
│   ├── discount_service.py    折扣
│   └── quote_schema.py        数据模型
├── data/
│   ├── product_series.json    系列 → 型号映射
│   ├── product_alias.json     客户叫法别名
│   ├── product_keyword_rules.json 关键词/颜色/配件规则
│   ├── product_category_map.json 分类映射
│   ├── accessory_directives.json 订单配件指令
│   ├── accessory_mapping.json WB → 预埋盒映射
│   └── products.json          产品数据（保留，不作为正式报价源）
├── templates/
│   └── index.html             首页（响应式）
├── static/
│   ├── app.js                 前端逻辑
│   └── style.css              响应式样式
├── output/
│   ├── *.xlsx                 生成的报价单
│   └── quote.db               SQLite 历史数据库
├── deploy/
│   ├── start_server.bat       单独启动 Flask
│   ├── start_tunnel.bat       单独启动 Tunnel
│   └── README.md              Cloudflare Tunnel 说明
└── logs/ temp/ uploads/       运行目录（可留空）
```

## 四、启动方法

### 依赖安装（首次）

```powershell
cd /d "E:\新建文件夹 (2)\灯具报价\KEEY_AI_Quote"
pip install -r requirements.txt
```

## 五、Flask 运行方式

```powershell
python app.py
```

启动后控制台输出：

```
==================================================
  KEEY AI 报价系统 已启动

  本机访问:  http://127.0.0.1:5000
  局域网访问: http://192.168.x.x:5000

  请确保手机与电脑连接同一 WiFi。
==================================================
```

- 本机访问：`http://127.0.0.1:5000`
- 局域网访问：`http://192.168.x.x:5000`

## 六、Cloudflare Tunnel 公网访问

### 前提

下载 `cloudflared-windows-amd64.exe`，改名为 `cloudflared.exe`，放入 `C:\Windows\System32`。

下载地址：

https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/

### 方式一：一键启动

双击 `start.bat`：

1. 自动启动 Flask（新窗口）
2. 等待 5 秒
3. 自动启动 Cloudflare Tunnel（新窗口）
4. 在 Tunnel 窗口查看 `https://xxxxx.trycloudflare.com`

### 方式二：手动

终端 1：

```powershell
python app.py
```

终端 2：

```powershell
cloudflared tunnel --url http://127.0.0.1:5000
```

手机通过 5G / WiFi 访问输出的公网 HTTPS 地址。

## 七、数据库说明

SQLite 数据库：`output/quote.db`

表结构：

### orders（报价主表）

| 字段 | 说明 |
|------|------|
| id | 自增主键 |
| customer | 客户名称 |
| project | 项目名称 |
| filename | 生成的 Excel 文件名 |
| total_amount | 原价合计 |
| discount | 折扣率 |
| final_amount | 应收金额 |
| create_time | 生成时间 |

### order_items（报价明细）

| 字段 | 说明 |
|------|------|
| id | 自增主键 |
| order_id | 外键 → orders.id |
| model | 产品型号 |
| name | 产品名称 |
| color | 颜色 |
| quantity | 数量 |
| unit_price | 单价 |
| total_price | 金额 |

首次启动自动建表（幂等），重复启动不会报错，不删除已有数据。

## 八、产品库维护方式

### 唯一数据源

```
D:\0000AAA报价助手\1.2026企一产品报价表(最新）.xlsx
```

### 报价模板

```
D:\0000AAA报价助手\2026.07.18-灯具报价单 .xlsx
```

### 新增/修改产品

1. 直接更新产品库 Excel
2. 重新运行映射生成工具：

```powershell
python build_series_mapping.py
```

3. 工具自动更新 `data/product_series.json` 的型号映射

### 预埋件映射

如新增 WB 产品，需同步维护：

```
data/accessory_mapping.json
```

格式：

```json
{
  "wb_to_zh": {
    "QY-WB06055S": "QY-ZH031MF-1"
  }
}
```

## 九、后续开发注意事项

### 不要修改的 V1 核心

- V1 Excel 引擎（`KEEY报价助手_V1.0_Stable_RESTORE/scripts/`）
- 产品库 Excel（正式报价数据源）
- 报价模板（图片、公式、红字、页面设置）

### 修改原则

1. **参数修改只走 `merge_product_params()`**：色温/光束角统一入口
2. **数据库查询只走 `exact_db_lookup()`**：精确查库，不用模糊搜索决定最终产品
3. **产品匹配遵循系列内匹配**：不允许跨系列返回产品
4. **新增系列只改 `data/product_series.json`**，不改业务代码
5. **新增配件规则只改 `data/accessory_mapping.json` / `accessory_directives.json`**

### 启动端口

Flask 固定监听 `0.0.0.0:5000`（已配置），Cloudflare Tunnel 指向 `http://127.0.0.1:5000`。

### 运行依赖

```
Flask
python-dotenv
openpyxl
```
