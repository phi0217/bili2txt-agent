# src 目录重构总结

## 重构日期
2026-03-09

## 重构概述

将所有 Python 源代码文件（除了 main.py）移动到 `src/` 目录，使项目结构更加清晰和专业。

## 主要变更

### 1. 目录结构变化

#### 重构前

```
bili2txt-agent/
├── main.py                 # 程序入口
├── config.py               # 配置管理
├── utils.py                # 通用工具
├── bilibili_utils.py       # 视频处理
├── audio_utils.py          # 音频提取
├── asr_utils.py            # 语音识别
├── llm_utils.py            # 文本精转
├── doc_utils.py            # 文档创建
├── feishu_handler.py       # 飞书消息
├── feishu_ws_client.py     # WebSocket 客户端
├── task.py                 # 任务处理
└── install-ffmpeg.ps1      # FFmpeg 安装
```

#### 重构后

```
bili2txt-agent/
├── main.py                 # 程序入口（根目录）
│
├── src/                    # 📦 源代码目录
│   ├── __init__.py         # 包初始化
│   ├── config.py           # 配置管理
│   ├── utils.py            # 通用工具
│   ├── bilibili_utils.py   # 视频处理
│   ├── audio_utils.py      # 音频提取
│   ├── asr_utils.py        # 语音识别
│   ├── llm_utils.py        # 文本精转
│   ├── doc_utils.py        # 文档创建
│   ├── feishu_handler.py   # 飞书消息
│   ├── feishu_ws_client.py # WebSocket 客户端
│   └── task.py             # 任务处理
│
└── install-ffmpeg.ps1      # FFmpeg 安装（根目录）
```

### 2. 文件移动

| 文件 | 原位置 | 新位置 |
|------|--------|--------|
| config.py | 根目录 | src/ |
| utils.py | 根目录 | src/ |
| bilibili_utils.py | 根目录 | src/ |
| audio_utils.py | 根目录 | src/ |
| asr_utils.py | 根目录 | src/ |
| llm_utils.py | 根目录 | src/ |
| doc_utils.py | 根目录 | src/ |
| feishu_handler.py | 根目录 | src/ |
| feishu_ws_client.py | 根目录 | src/ |
| task.py | 根目录 | src/ |
| main.py | 根目录 | **根目录（保持不变）** |

### 3. 新增文件

- **src/__init__.py** - Python 包初始化文件

### 4. 导入路径更新

#### main.py

**更新前**：
```python
from config import config
from utils import setup_logging
from feishu_ws_client import start_feishu_ws
```

**更新后**：
```python
import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config import config
from utils import setup_logging
from feishu_ws_client import start_feishu_ws
```

#### 测试文件

所有测试文件（`tests/test_*.py`）都添加了路径配置：

```python
import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import config
```

### 5. 文档更新

- [x] README.md - 更新项目结构图
- [x] docs/PROJECT_STRUCTURE.md - 更新目录结构说明

## 优势

### 1. 更清晰的项目结构

- ✅ 根目录只保留启动文件（main.py）
- ✅ 所有源代码集中在 src/ 目录
- ✅ 文档和测试独立在外

### 2. 更好的组织

- ✅ 符合 Python 项目标准结构
- ✅ 便于打包和分发
- ✅ 更容易理解项目组成

### 3. 更好的导入管理

- ✅ 统一的导入路径
- ✅ 明确的包结构
- ✅ 便于相对导入

## 兼容性

### 内部导入

src/ 目录内部的模块之间导入**保持不变**：

```python
# src/task.py
from config import config          # ✅ 不变
from utils import cleanup_files    # ✅ 不变
from bilibili_utils import download_video  # ✅ 不变
```

### 外部导入

从项目外部导入需要添加路径：

```python
import sys
import os
sys.path.insert(0, 'path/to/bili2txt-agent/src')

from config import config
from task import process_video_sync
```

## 运行方式

### 启动项目（无变化）

```bash
# 在项目根目录
python main.py
```

### 运行测试（无变化）

```bash
# 在 tests/ 目录
python test_short_link.py
python test_simple_write.py
python test_document_api.py
```

## 影响范围

### 无影响的保证

- ✅ 所有功能保持不变
- ✅ 配置文件格式不变
- ✅ 环境变量不变
- ✅ 运行方式不变
- ✅ 测试脚本正常运行

### 需要注意

- ⚠️ 如果有外部脚本导入项目模块，需要更新导入路径
- ⚠️ IDE 可能需要重新索引项目

## 后续建议

### 1. 使用相对导入（可选）

如果需要更规范的包结构，可以改用相对导入：

```python
# src/task.py
from .config import config
from .utils import cleanup_files
```

### 2. 添加 __main__.py（可选）

让 src/ 成为一个可直接运行的包：

```python
# src/__main__.py
from ..main import main

if __name__ == '__main__':
    main()
```

### 3. 创建 setup.py（可选）

如果需要打包分发：

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name='bili2txt-agent',
    packages=find_packages(),
    # ...
)
```

## 验证清单

- [x] 创建 src/ 目录
- [x] 移动所有 Python 文件（除 main.py）
- [x] 创建 src/__init__.py
- [x] 更新 main.py 导入路径
- [x] 更新所有测试文件导入路径
- [x] 更新 README.md 项目结构
- [x] 更新 docs/PROJECT_STRUCTURE.md
- [x] 验证功能正常运行

## 文件清单

### 移动的文件（10个）

- [x] config.py → src/config.py
- [x] utils.py → src/utils.py
- [x] bilibili_utils.py → src/bilibili_utils.py
- [x] audio_utils.py → src/audio_utils.py
- [x] asr_utils.py → src/asr_utils.py
- [x] llm_utils.py → src/llm_utils.py
- [x] doc_utils.py → src/doc_utils.py
- [x] feishu_handler.py → src/feishu_handler.py
- [x] feishu_ws_client.py → src/feishu_ws_client.py
- [x] task.py → src/task.py

### 新增的文件（1个）

- [x] src/__init__.py

### 更新的文件（5个）

- [x] main.py
- [x] tests/test_document_api.py
- [x] tests/test_short_link.py
- [x] tests/test_simple_write.py
- [x] README.md

## 总结

本次重构：

✅ **提升项目结构** - 符合 Python 标准项目布局
✅ **保持功能完整** - 所有功能正常运行
✅ **零破坏性变更** - 运行方式完全不变
✅ **便于维护扩展** - 清晰的目录组织

项目现在拥有：
- 📦 标准的 src/ 源代码目录
- 🚀 简洁的根目录（只有 main.py）
- 📚 完整的文档体系
- 🧪 独立的测试目录

---

**重构日期**: 2026-03-09
**版本**: 1.1.0
**维护**: bili2txt-agent 项目组
