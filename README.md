<p align="center">
  <h1 align="center"> TokenForge-CLI</h1>
  <p align="center"><strong>Lightweight Terminal LLM Token Intelligent Compression Engine</strong></p>
  <p align="center">轻量级终端LLM Token智能压缩引擎</p>
</p>

<p align="center">
  <a href="#-简体中文"><img src="https://img.shields.io/badge/简体中文-blue" alt="简体中文"></a>
  <a href="#-繁體中文"><img src="https://img.shields.io/badge/繁體中文-blue" alt="繁體中文"></a>
  <a href="#-english"><img src="https://img.shields.io/badge/English-blue" alt="English"></a>
  <br><br>
  <img src="https://img.shields.io/badge/Python-3.8+-green" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/Zero_Dependencies-✓-success" alt="Zero Dependencies">
  <img src="https://img.shields.io/badge/License-MIT-informational" alt="MIT License">
  <img src="https://img.shields.io/badge/Version-1.0.0-orange" alt="v1.0.0">
</p>

---

## 🎉 项目介绍

**TokenForge-CLI** 是一款零依赖、纯Python实现的轻量级终端LLM Token智能压缩引擎。它通过6种智能压缩策略，帮助开发者在使用大语言模型时显著降低Token消耗，节省API调用成本。

### 💡 灵感来源

随着LLM应用的爆发式增长，Token成本成为开发者面临的核心痛点。TokenForge-CLI参考了GitHub Trending上热门的LLM输入压缩工具的产品理念，但采用完全独立自研的技术方案，特别针对中文文本场景进行了深度优化。

### 🔥 自研差异化亮点

- **中文特化压缩** — 专门针对中文文本的冗余表达模式进行优化，去除"众所周知""事实上""进行一下分析"等冗余句式
- **零外部依赖** — 纯Python标准库实现，无需安装任何第三方包，开箱即用
- **6种压缩策略** — 关键词提取、语义去重、结构化压缩、模板缩写、分块优化、中文优化
- **TUI可视化仪表盘** — 终端内实时展示压缩效果、管道流程、节省率仪表
- **多格式导出** — 支持JSON、CSV、Markdown、纯文本格式的报告导出
- **批量处理** — 支持多文件批量压缩，生成汇总报告

---

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🎯 **6种压缩策略** | 关键词提取、语义去重、结构化压缩、模板缩写、分块优化、中文优化 |
| 🇨🇳 **中文特化** | 专门优化中文冗余表达，支持中英混合文本 |
| 📊 **Token估算** | 基于字符级启发式算法，支持多语言Token估算 |
| 🖥️ **TUI仪表盘** | 美观的终端可视化面板，实时展示压缩效果 |
| 📦 **零依赖** | 纯Python标准库，无需pip install |
| 🔄 **批量处理** | 支持多文件批量压缩 |
| 📤 **多格式导出** | JSON / CSV / Markdown / 纯文本 |
| ⚡ **可调强度** | 0.0-1.0压缩强度，灵活控制压缩比例 |
| 🔀 **管道式架构** | 策略可组合、可排序、可单独使用 |
| 📐 **对比视图** | 原文与压缩文本并排对比 |

---

## 🚀 快速开始

### 环境要求

- **Python 3.8+** （无需任何第三方依赖）

### 安装

```bash
# 克隆仓库
git clone https://github.com/gitstq/TokenForge-CLI.git
cd TokenForge-CLI

# 无需安装依赖，直接使用
python tokenslim.py --version
```

### 基本使用

```bash
# 压缩文本（从命令行输入）
echo "你的长文本..." | python tokenslim.py compress

# 压缩文件
python tokenslim.py compress -f input.txt

# 指定压缩强度（0.0-1.0）
python tokenslim.py compress -f input.txt -i 0.8

# 使用特定策略
python tokenslim.py compress -f input.txt -s "template,chinese_optimization"

# 仅输出压缩后的文本
python tokenslim.py compress -f input.txt -q

# 导出报告
python tokenslim.py compress -f input.txt -o report.json --format json
python tokenslim.py compress -f input.txt -o report.md --format markdown
```

### Token估算

```bash
# 估算文本Token数
echo "Hello world" | python tokenslim.py estimate

# 详细估算（含语言分布）
python tokenslim.py estimate -f document.txt -d
```

### 批量处理

```bash
# 批量压缩多个文件
python tokenslim.py batch file1.txt file2.txt file3.txt

# 批量压缩并导出报告
python tokenslim.py batch *.txt -o batch_report.csv --format csv
```

### 对比视图

```bash
# 原文与压缩文本并排对比
python tokenslim.py compare -f document.txt
```

### 查看可用策略

```bash
python tokenslim.py strategies
python tokenslim.py strategies --json
```

---

## 📖 详细使用指南

### 压缩策略详解

| 策略名称 | 类别 | 说明 |
|----------|------|------|
| `keyword_extraction` | 语义 | 提取关键句子和短语，去除填充词（如"众所周知""it is important to note that"） |
| `semantic_dedup` | 语义 | 基于字符N-gram相似度去除语义重复内容 |
| `structured` | 结构 | 压缩代码块注释、编号列表、结构化内容 |
| `template` | 结构 | 将冗长表达替换为缩写模板（如"artificial intelligence"→"AI"） |
| `chunk_optimization` | 结构 | 基于段落重要性评分优化分块，适配LLM上下文窗口 |
| `chinese_optimization` | 语言 | 专门去除中文冗余表达（如"进行一下分析"→"分析"） |

### 压缩强度说明

| 强度值 | 效果 | 适用场景 |
|--------|------|----------|
| 0.1-0.3 | 轻度压缩，保留最多原始信息 | 需要高保真的场景 |
| 0.4-0.6 | 中度压缩，平衡效果与保留率 | 日常使用推荐 |
| 0.7-0.9 | 高强度压缩，最大化Token节省 | 成本敏感场景 |
| 1.0 | 最高强度，激进压缩 | 对信息保留要求低的场景 |

### 输出格式

```bash
# JSON格式（适合程序处理）
python tokenslim.py compress -f doc.txt --format json

# CSV格式（适合表格分析）
python tokenslim.py compress -f doc.txt --format csv

# Markdown格式（适合文档报告）
python tokenslim.py compress -f doc.txt --format markdown

# 纯文本格式（默认）
python tokenslim.py compress -f doc.txt --format text
```

---

## 💡 设计思路与迭代规划

### 设计理念

TokenForge-CLI遵循以下核心设计原则：

1. **零依赖哲学** — 不引入任何第三方包，确保在任何Python环境下都能直接运行
2. **管道式架构** — 每种压缩策略独立实现，可自由组合、排序、替换
3. **语言感知** — 自动检测文本语言组成，针对不同语言采用不同的Token估算系数
4. **渐进式压缩** — 通过intensity参数精确控制压缩强度，满足不同场景需求

### 技术选型

- **纯Python标准库** — 使用`re`、`json`、`csv`、`argparse`等标准模块
- **字符N-gram相似度** — 用于语义去重，无需向量模型
- **启发式评分** — 基于信息密度的段落重要性评分

### 后续迭代计划

- [ ] 添加MCP Server模式，作为AI Agent的压缩工具
- [ ] 支持HTTP Proxy模式，透明压缩LLM API请求
- [ ] 添加更多语言的特化压缩策略（日语、韩语）
- [ ] 支持自定义压缩模板配置文件
- [ ] 添加交互式TUI模式

---

## 📦 打包与部署

### 作为独立脚本使用

```bash
# 直接下载单文件使用
curl -O https://raw.githubusercontent.com/gitstq/TokenForge-CLI/main/tokenslim.py
python tokenslim.py compress -f your_file.txt
```

### 作为模块导入

```python
import sys
sys.path.insert(0, "TokenForge-CLI")

from src.compression import CompressionEngine
from src.token_estimator import TokenEstimator

# 压缩文本
engine = CompressionEngine()
compressed, stats = engine.compress("你的长文本...", intensity=0.6)
print(f"Token节省: {stats['token_saved_percent']}%")

# 估算Token
tokens = TokenEstimator.estimate("Hello world 你好世界")
print(f"估算Token数: {tokens}")
```

### 兼容环境

| 环境 | 支持情况 |
|------|----------|
| Python 3.8+ | ✅ 完全支持 |
| Python 3.7 | ⚠️ 部分功能可用 |
| Windows | ✅ 支持 |
| macOS | ✅ 支持 |
| Linux | ✅ 支持 |

---

## 🤝 贡献指南

欢迎贡献代码！请遵循以下规范：

### 提交规范

使用Angular提交规范：

```
feat: 新增XXX功能
fix: 修复XXX问题
docs: 更新XXX文档
refactor: 重构XXX模块
test: 新增XXX测试
chore: 更新XXX配置
```

### Issue反馈

1. 描述问题或功能建议
2. 提供复现步骤（如适用）
3. 附上环境信息（Python版本、操作系统）

### PR提交流程

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/your-feature`)
3. 提交更改 (`git commit -m 'feat: add your feature'`)
4. 推送分支 (`git push origin feature/your-feature`)
5. 创建Pull Request

---

## 📄 开源协议

本项目基于 [MIT License](LICENSE) 开源。

---

<p align="center">
  Made with 🦞 by <a href="https://github.com/gitstq">gitstq</a>
</p>

---

## 🇹🇼 繁體中文

### 🎉 專案介紹

**TokenForge-CLI** 是一款零依賴、純Python實作的輕量級終端LLM Token智慧壓縮引擎。它透過6種智慧壓縮策略，幫助開發者在大型語言模型應用中顯著降低Token消耗，節省API呼叫成本。

### 💡 靈感來源

隨著LLM應用的爆發式增長，Token成本成為開發者面臨的核心痛點。TokenForge-CLI參考了GitHub Trending上熱門的LLM輸入壓縮工具的產品理念，但採用完全獨立自研的技術方案，特別針對中文文本場景進行了深度優化。

### 🔥 自研差異化亮點

- **中文特化壓縮** — 專門針對中文文本的冗餘表達模式進行優化
- **零外部依賴** — 純Python標準庫實現，無需安裝任何第三方套件
- **6種壓縮策略** — 關鍵詞提取、語義去重、結構化壓縮、模板縮寫、分塊優化、中文優化
- **TUI視覺化儀表板** — 終端內即時展示壓縮效果
- **多格式匯出** — 支援JSON、CSV、Markdown、純文字格式
- **批次處理** — 支援多檔案批次壓縮

### ✨ 核心特性

| 特性 | 說明 |
|------|------|
| 🎯 **6種壓縮策略** | 關鍵詞提取、語義去重、結構化壓縮、模板縮寫、分塊優化、中文優化 |
| 🇨🇳 **中文特化** | 專門優化中文冗餘表達，支援中英混合文本 |
| 📊 **Token估算** | 基於字元級啟發式演算法，支援多語言Token估算 |
| 🖥️ **TUI儀表板** | 美觀的終端視覺化面板 |
| 📦 **零依賴** | 純Python標準庫，無需pip install |
| 🔄 **批次處理** | 支援多檔案批次壓縮 |
| 📤 **多格式匯出** | JSON / CSV / Markdown / 純文字 |

### 🚀 快速開始

```bash
# 克隆倉庫
git clone https://github.com/gitstq/TokenForge-CLI.git
cd TokenForge-CLI

# 無需安裝依賴，直接使用
python tokenslim.py --version
```

```bash
# 壓縮文字（從命令列輸入）
echo "你的長文本..." | python tokenslim.py compress

# 壓縮檔案
python tokenslim.py compress -f input.txt

# 指定壓縮強度（0.0-1.0）
python tokenslim.py compress -f input.txt -i 0.8

# 僅輸出壓縮後的文字
python tokenslim.py compress -f input.txt -q

# 匯出報告
python tokenslim.py compress -f input.txt -o report.json --format json
```

### 📖 詳細使用指南

#### 壓縮策略詳解

| 策略名稱 | 類別 | 說明 |
|----------|------|------|
| `keyword_extraction` | 語義 | 提取關鍵句子和短語，去除填充詞 |
| `semantic_dedup` | 語義 | 基於字元N-gram相似度去除語義重複內容 |
| `structured` | 結構 | 壓縮程式碼區塊註解、編號列表、結構化內容 |
| `template` | 結構 | 將冗長表達替換為縮寫模板 |
| `chunk_optimization` | 結構 | 基於段落重要性評分優化分塊 |
| `chinese_optimization` | 語言 | 專門去除中文冗餘表達 |

### 💡 設計思路與迭代規劃

#### 設計理念

1. **零依賴哲學** — 不引入任何第三方套件
2. **管道式架構** — 每種壓縮策略獨立實現，可自由組合
3. **語言感知** — 自動偵測文本語言組成
4. **漸進式壓縮** — 透過intensity參數精確控制壓縮強度

### 📦 打包與部署

```bash
# 作為獨立腳本使用
curl -O https://raw.githubusercontent.com/gitstq/TokenForge-CLI/main/tokenslim.py
python tokenslim.py compress -f your_file.txt
```

```python
# 作為模組匯入
from src.compression import CompressionEngine

engine = CompressionEngine()
compressed, stats = engine.compress("你的長文本...", intensity=0.6)
print(f"Token節省: {stats['token_saved_percent']}%")
```

### 🤝 貢獻指南

歡迎貢獻程式碼！請遵循Angular提交規範。

### 📄 開源協議

本專案基於 [MIT License](LICENSE) 開源。

---

## 🇺🇸 English

### 🎉 Project Introduction

**TokenForge-CLI** is a zero-dependency, pure Python lightweight terminal LLM token intelligent compression engine. It helps developers significantly reduce token consumption when using large language models through 6 intelligent compression strategies, saving API call costs.

### 💡 Inspiration

With the explosive growth of LLM applications, token costs have become a core pain point for developers. TokenForge-CLI draws inspiration from popular LLM input compression tools on GitHub Trending, but implements a fully independent technical solution with deep optimization specifically for Chinese text scenarios.

### 🔥 Differentiation Highlights

- **Chinese-Optimized Compression** — Specially optimized for redundant expression patterns in Chinese text
- **Zero Dependencies** — Pure Python standard library, no third-party packages needed
- **6 Compression Strategies** — Keyword extraction, semantic dedup, structured compression, template abbreviation, chunk optimization, Chinese optimization
- **TUI Visual Dashboard** — Real-time compression visualization in terminal
- **Multi-Format Export** — JSON, CSV, Markdown, plain text
- **Batch Processing** — Multi-file batch compression support

### ✨ Core Features

| Feature | Description |
|---------|-------------|
| 🎯 **6 Strategies** | Keyword extraction, semantic dedup, structured, template, chunk optimization, Chinese optimization |
| 🇨🇳 **Chinese Specialized** | Optimized for Chinese redundant expressions, supports mixed CJK-English text |
| 📊 **Token Estimation** | Character-level heuristic algorithm for multi-language token estimation |
| 🖥️ **TUI Dashboard** | Beautiful terminal visualization panel with real-time stats |
| 📦 **Zero Dependencies** | Pure Python standard library, no pip install required |
| 🔄 **Batch Processing** | Multi-file batch compression |
| 📤 **Multi-Format Export** | JSON / CSV / Markdown / Plain Text |
| ⚡ **Adjustable Intensity** | 0.0-1.0 compression intensity for flexible control |
| 🔀 **Pipeline Architecture** | Strategies are composable, orderable, and independently usable |

### 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/gitstq/TokenForge-CLI.git
cd TokenForge-CLI

# No dependencies to install, use directly
python tokenslim.py --version
```

```bash
# Compress text (from stdin)
echo "Your long text..." | python tokenslim.py compress

# Compress a file
python tokenslim.py compress -f input.txt

# Specify compression intensity (0.0-1.0)
python tokenslim.py compress -f input.txt -i 0.8

# Use specific strategies
python tokenslim.py compress -f input.txt -s "template,chinese_optimization"

# Output only compressed text
python tokenslim.py compress -f input.txt -q

# Export report
python tokenslim.py compress -f input.txt -o report.json --format json
python tokenslim.py compress -f input.txt -o report.md --format markdown
```

### 📖 Detailed Usage Guide

#### Strategy Reference

| Strategy | Category | Description |
|----------|----------|-------------|
| `keyword_extraction` | Semantic | Extract key sentences, remove filler phrases |
| `semantic_dedup` | Semantic | Remove semantically duplicate content via character N-gram similarity |
| `structured` | Structural | Compress code block comments, numbered lists, structured content |
| `template` | Structural | Replace verbose expressions with abbreviation templates |
| `chunk_optimization` | Structural | Optimize chunking based on paragraph importance scoring |
| `chinese_optimization` | Language | Remove Chinese-specific redundant expressions |

#### Intensity Guide

| Intensity | Effect | Use Case |
|-----------|--------|----------|
| 0.1-0.3 | Light compression, maximum preservation | High-fidelity scenarios |
| 0.4-0.6 | Medium compression, balanced | Recommended for daily use |
| 0.7-0.9 | High compression, maximum savings | Cost-sensitive scenarios |
| 1.0 | Maximum compression | Low preservation requirements |

### 💡 Design Philosophy

1. **Zero Dependency** — No third-party packages, runs in any Python environment
2. **Pipeline Architecture** — Each strategy is independently implemented and freely composable
3. **Language Aware** — Auto-detects text language composition with per-language token estimation
4. **Progressive Compression** — Precise control via intensity parameter

### 📦 Deployment

```bash
# Use as standalone script
curl -O https://raw.githubusercontent.com/gitstq/TokenForge-CLI/main/tokenslim.py
python tokenslim.py compress -f your_file.txt
```

```python
# Import as module
from src.compression import CompressionEngine
from src.token_estimator import TokenEstimator

engine = CompressionEngine()
compressed, stats = engine.compress("Your long text...", intensity=0.6)
print(f"Token saved: {stats['token_saved_percent']}%")

tokens = TokenEstimator.estimate("Hello world")
print(f"Estimated tokens: {tokens}")
```

### 🤝 Contributing

Contributions are welcome! Please follow Angular commit conventions.

### 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
  Made with 🦞 by <a href="https://github.com/gitstq">gitstq</a>
</p>
