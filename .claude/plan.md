# ObjectBox 数据库浏览器实现计划

## Context

用户需要一个通用的 ObjectBox 数据库浏览器，能够浏览 `data.mdb` 文件中的所有数据，无需硬编码实体类型。当前项目 `src/db.py` 仅实现了针对特定前缀的读取功能（Reqable 应用的捕获记录），需要扩展为通用的浏览器工具。

**关键发现：**
- ObjectBox 使用 LMDB 作为底层存储
- 数据键格式：`[4字节前缀][4字节实体ID]`
- 前缀计算公式：`数据前缀 = 0x18000000 + (entity_id * 4)`
- Schema 信息存储在特殊前缀 `00 00 00 00` 下
- 数据格式：FlatBuffers 序列化 或 gzip+base64 编码的 JSON
- 当前数据库包含 5 个实体类型，约 53,866 条记录

## 实现方案

### 技术栈选择（已确认）

**GUI 库：CustomTkinter** ✅
- 现代外观、基于 tkinter（无需复杂安装）、适合数据浏览工具
- 表格控件：使用 `tkinter.ttk.Treeview` 进行数据展示
- 对比 PyQt6/PySide6：更轻量、无许可证问题、开发速度更快

**数据访问层：扩展现有 `db.py`**
- 添加动态实体发现功能
- 实现通用的数据解码策略
- 提供 Read + Delete 接口（只读浏览 + 删除功能）✅

**导出功能：导出为 JSON** ✅
- 支持单条记录导出
- 支持批量导出选中记录

### 项目结构

```
ObjectBoxViewer/
├── src/
│   ├── db.py              # 扩展：添加通用 CRUD 方法
│   ├── schema.py          # 新增：Schema 发现和解析
│   ├── decoder.py         # 新增：数据解码器
│   └── gui/
│       ├── __init__.py
│       ├── main_window.py # 主窗口（文件选择 + 表列表）
│       ├── table_view.py  # 数据表格视图
│       ├── detail_view.py # 记录详情查看
│       └── styles.py      # UI 样式配置
├── main.py                # 应用入口
└── requirements.txt       # 依赖：lmdb, customtkinter
```

### 核心功能模块

#### 1. Schema 发现模块 (`src/schema.py`)

**功能：**
- 扫描 `00 00 00 00` 前缀的 Schema 记录
- 解析实体名称和 ID
- 计算数据前缀和索引前缀

**关键方法：**
```python
def discover_entities(env: lmdb.Environment) -> dict[int, EntityInfo]
def get_entity_count(env: lmdb.Environment, prefix: bytes) -> int
```

#### 2. 数据解码模块 (`src/decoder.py`)

**解码策略（优先级）：**
1. 尝试 gzip + base64 解码为 JSON
2. 提取嵌入的 JSON 对象
3. 返回原始 FlatBuffers 数据（标记为需 schema）

**关键方法：**
```python
def decode_value(raw: bytes) -> dict | None
def try_gzip_b64_decode(raw: bytes) -> dict | None
def extract_embedded_json(raw: bytes) -> list[dict]
```

#### 3. 扩展 db.py

**新增方法：**
```python
# 通用迭代器
def iter_entity(self, entity_id: int) -> Generator[tuple[int, dict], None, None]

# Read + Delete 操作
def list_entities(self) -> dict[int, EntityInfo]
def get_record(self, entity_id: int, record_id: int) -> dict | None
def delete_record(self, entity_id: int, record_id: int) -> bool
```

#### 4. GUI 模块 (`src/gui/`)

**主窗口 (main_window.py):**
- 顶部：文件选择器（Entry + Button）
- 左侧：实体列表（Treeview，显示实体名称和记录数）
- 右侧：数据表格（Treeview，显示选中实体的数据）
- 底部：状态栏（显示总记录数、当前选中记录）

**表格视图 (table_view.py):**
- 动态列：根据数据字段自动生成
- 支持排序（点击列标题）
- 支持滚动（虚拟滚动优化大数据）
- 双击记录打开详情窗口

**详情视图 (detail_view.py):**
- JSON 格式化显示
- 支持复制到剪贴板
- 支持导出为文件

**样式配置 (styles.py):**
- CustomTkinter 主题配置
- 表格样式（字体、颜色、行高）
- 响应式布局

### 实现步骤

**Phase 1: 核心数据层（优先）**
1. 创建 `src/schema.py` - 实现实体发现功能
2. 创建 `src/decoder.py` - 实现数据解码器
3. 扩展 `src/db.py` - 添加通用 CRUD 方法

**Phase 2: GUI 框架**
4. 创建 `src/gui/styles.py` - 配置 CustomTkinter 样式
5. 创建 `src/gui/main_window.py` - 主窗口布局
6. 创建 `src/gui/table_view.py` - 数据表格组件
7. 创建 `src/gui/detail_view.py` - 详情查看组件

**Phase 3: 集成和优化**
8. 创建 `main.py` - 应用入口
9. 创建 `requirements.txt` - 依赖管理
10. 测试和优化（大数据量性能、UI 响应）

### 关键文件和修改

**修改文件：**
- `src/db.py` - 添加 5 个新方法（list_entities, iter_entity, get_record, delete_record, create_record）

**新增文件：**
- `src/schema.py` - 实体发现和 Schema 解析
- `src/decoder.py` - 数据解码逻辑
- `src/gui/main_window.py` - 主窗口
- `src/gui/table_view.py` - 表格视图
- `src/gui/detail_view.py` - 详情视图
- `src/gui/styles.py` - 样式配置
- `main.py` - 应用入口
- `requirements.txt` - 依赖列表

**测试数据：**
- 使用项目根目录的 `data.mdb`（约 388MB，53,866 条记录）

### 验证方案

**功能测试：**
1. 打开 `data.mdb` 文件，验证能否正确列出所有实体
2. 选择 `CaptureRecordHistoryEntity`，验证能否正确加载 24,756 条记录
3. 双击记录，验证详情窗口是否正确显示 JSON 数据
4. 测试删除记录功能（需确认对话框）
5. 测试文件切换功能（打开不同的 .mdb 文件）

**性能测试：**
1. 加载 24,756 条记录的响应时间（目标 < 2 秒）
2. 滚动流畅度（使用虚拟滚动）
3. 内存占用（目标 < 500MB）

**UI 测试：**
1. 窗口缩放响应
2. 深色/浅色主题切换
3. 文件选择对话框集成

### 风险和限制

**技术限制：**
1. **Create/Update 操作受限**：FlatBuffers 需要编译 schema 文件，建议仅实现 Read + Delete
2. **大数据量性能**：超过 10 万条记录可能需要分页加载
3. **数据格式未知**：部分 FlatBuffers 数据无法解码（无 schema）

**应对策略：**
1. 默认只读模式，Delete 操作需要明确确认
2. 实现虚拟滚动和懒加载
3. 对无法解码的数据显示原始字节（十六进制）

## 依赖项

```
lmdb>=1.4.1
customtkinter>=5.2.0
```

## 交付物

1. 完整的 ObjectBox 浏览器应用
2. 支持动态加载任意 .mdb 文件
3. 自动发现所有实体类型
4. 数据浏览、搜索、导出功能
5. 现代化 GUI 界面
