# Yambda Music Behavior Analysis & ML System

基于 Yambda 用户音乐行为日志的多事件行为分析、机器学习建模与可视化大屏系统

## 项目概述

本项目是一个综合性数据科学与机器学习实践项目，包含数据分析、特征工程、机器学习建模和可视化系统。

### 核心功能模块

- **模块 0**: 数据总览与描述性分析
- **模块 1**: 数据预处理与特征工程
- **模块 2**: 歌曲内容聚类（KMeans，无监督学习）
- **模块 3**: 播放完成率预测（RandomForest，监督学习）
- **模块 4**: 异常用户检测（Isolation Forest，无监督异常检测）
- **模块 5**: REST API 后端（Flask）
- **模块 6**: 可视化大屏系统（ECharts + CSS Grid）

## 数据集

**数据来源**: Yambda Music Recommendation Dataset (Deezer/Yandex)
- HuggingFace: `yandex/yambda`, `flat-multievent-50m`
- 包含用户音乐行为日志（播放、点赞、点踩等）
- 包含歌曲音频嵌入向量

**注**: 本项目自动生成示例数据用于演示，也支持从 HuggingFace 加载真实数据集。

## 技术栈

- **数据处理**: Python, Pandas, NumPy
- **机器学习**: scikit-learn (KMeans, RandomForest, Isolation Forest, PCA)
- **数据存储**: SQLite
- **后端**: Flask, Flask-CORS
- **前端**: HTML, CSS Grid, JavaScript
- **可视化**: ECharts 5.4.3

## 项目结构

```
music/
├── app.py                  # Flask 后端 API
├── run.py                  # 主执行脚本
├── requirements.txt        # Python 依赖
├── scripts/
│   ├── data_loader.py      # 数据加载与预处理
│   └── ml_modules.py       # 机器学习模块
├── static/
│   ├── index.html          # 主页面
│   ├── css/
│   │   └── style.css       # Morandi 配色样式
│   └── js/
│       └── dashboard.js    # 数据可视化逻辑
├── data/                   # 数据存储目录
│   ├── *.parquet           # Parquet 数据文件
│   └── yambda.db           # SQLite 数据库
└── models/                 # 模型存储目录
    ├── *.pkl               # 训练好的模型
    ├── *.csv               # 分析结果
    └── *.json              # 评估指标
```

## 安装与运行

### 快速启动（推荐）

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 一键启动（自动运行数据处理和启动服务）
./start.sh
# 或
bash start.sh
```

然后在浏览器中访问: http://localhost:5001

### 分步运行

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 运行完整流程

```bash
python run.py
```

这将依次执行：
- 数据加载与预处理
- 特征工程
- 机器学习模型训练
- 结果存储

#### 3. 启动可视化大屏

```bash
python app.py
```

然后在浏览器中访问: http://localhost:5001

## 机器学习模块详解

### 模块 2: 歌曲聚类（无监督学习）

**目标**: 基于音频嵌入探索音乐内容的特征空间结构

**特征**:
- 歌曲 normalized_embed（64维，PCA降至10维）

**算法**: KMeans
- 使用轮廓系数选择最优 k 值
- 分析不同聚类的播放完成率和点赞比例差异

**评估**: Silhouette Score

### 模块 3: 播放完成率预测（监督学习）

**目标**: 预测用户对歌曲的播放完成率

**特征**:
- track_length_seconds (曲目长度)
- avg_completion_rate_user (用户平均完成率)
- like_ratio_user (用户点赞比例)
- behavior_diversity (用户行为多样性)
- avg_completion_rate_track (曲目平均完成率)
- like_ratio_track (曲目点赞比例)
- embed_0 to embed_4 (PCA降维后的嵌入)

**算法**: RandomForestRegressor
- 100棵决策树，最大深度10

**评估**: MAE, RMSE
- 输出特征重要性分析

### 模块 4: 异常用户检测（无监督异常检测）

**目标**: 识别异常播放行为模式的用户

**特征**:
- plays_per_hour (单位时间播放次数)
- total_events (总事件数)
- completion_variance (播放完成率方差)
- avg_interval_seconds (平均播放间隔)
- avg_completion_rate (平均完成率)
- behavior_diversity (行为多样性)

**算法**: Isolation Forest
- contamination=0.05 (5%异常率)

**分析**: 对比正常用户与异常用户的行为特征差异

## 可视化大屏设计

### 布局规范

- **Grid 系统**: 12列 × 6行
- **行高比例**: 3.5 : 10 : 10 : 10 : 10 : 2
- **无滚动**: 单屏展示所有内容

### 视觉规范

- **配色**: Morandi 莫兰迪色系（低饱和度）
  - 主色: #7d9d9c (青绿)
  - 辅助色: #b08b7a (赤陶)
  - 背景: #d4cfc9 (米色)
- **卡片**: 无圆角，1px描边，无阴影
- **动效**: 淡入动画，数值递增效果

### 图表类型

- 饼图: 事件分布、聚类分布、异常检测
- 柱状图: 完成率分布
- 组合图: 聚类分析（柱状+折线）
- 横向柱状图: 特征重要性

## API 接口

### 数据接口

- `GET /api/stats` - 总览统计
- `GET /api/overview` - 详细数据概览
- `GET /api/event-distribution` - 事件类型分布
- `GET /api/completion-distribution` - 完成率分布

### 聚类接口

- `GET /api/clustering/results` - 聚类分析结果
- `GET /api/clustering/distribution` - 聚类分布

### 预测接口

- `GET /api/prediction/metrics` - 预测模型指标
- `GET /api/prediction/feature-importance` - 特征重要性

### 异常检测接口

- `GET /api/anomaly/summary` - 异常检测摘要
- `GET /api/anomaly/distribution` - 异常分数分布

### 用户行为接口

- `GET /api/user-behavior/profile` - 用户行为画像
- `GET /api/user-behavior/diversity-distribution` - 行为多样性分布

## 使用 HuggingFace 真实数据集

如需使用真实的 Yambda 数据集：

1. 登录 HuggingFace:
```bash
huggingface-cli login
```

2. 修改 `scripts/data_loader.py` 中的 `__main__` 部分，取消注释数据集加载代码

3. 运行数据加载:
```bash
python scripts/data_loader.py
```

注意: 真实数据集较大，建议使用足够的存储空间和内存。

## 项目特点

✅ **完整的机器学习流程**: 从数据预处理到模型评估
✅ **多种学习范式**: 监督学习、无监督学习、异常检测
✅ **特征工程**: 用户级和曲目级特征构建
✅ **模型可解释性**: 特征重要性分析、聚类分析
✅ **专业可视化**: Morandi配色大屏系统
✅ **RESTful API**: 前后端分离架构

## 教学价值

本项目适用于：
- 数据科学课程实践
- 机器学习方法应用
- 数据可视化设计
- 全栈开发实践

## 许可证

本项目仅用于教学和研究目的。数据集来自 Yandex/Deezer 的 Yambda 开源数据集。

## 作者

Among the Mountain / 2024