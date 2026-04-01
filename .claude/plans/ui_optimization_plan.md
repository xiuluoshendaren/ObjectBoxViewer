# UI 优化计划

## 目标
1. 修复搜索后状态栏记录数显示问题
2. 更换 UI 风格，解决界面太黑的问题

## 当前问题

### 问题 1：搜索后状态栏记录数显示不正确
- 当前行为：搜索后右下角显示的是总记录数，而不是搜索结果数量
- 预期行为：搜索后应该显示搜索结果数量，例如 "Records: 50 / 1000 (filtered)"

**定位：**
- `src/gui/main_window.py` 的 `update_search_status` 方法
- `src/gui/table_view.py` 调用搜索过滤时需要正确更新状态

### 问题 2：界面风格太黑，对比度不足
- 当前配色：背景 `#2d2d2d`，偏暗
- 问题：整体色调过暗，长时间使用眼睛疲劳
- 需要调整为更明亮的配色方案

## 修改方案

### 修改 1：修复状态栏记录数显示

**文件：** `src/gui/table_view.py`

在 `_apply_search_filter` 方法中，搜索完成后调用主窗口的 `update_search_status` 方法更新状态栏。

**检查：**
- 确保 `_apply_search_filter` 调用 `update_search_status`
- 确保 `update_search_status` 正确接收参数并更新显示

### 修改 2：调整 UI 配色方案

**文件：** `src/gui/styles.py`

**配色方案调整：**

**方案：明亮灰蓝色主题**
- 背景主色：`#3a3f4b`（灰蓝色）
- 背景浅色：`#4a505c`（更浅的灰蓝）
- 行交替色：`#404650` / `#363c48`
- 文字主色：`#e8eaed`（接近白色）
- 文字浅色：`#b8bbbf`（浅灰色）
- 强调色：`#5dade2`（明亮蓝色）

**字体对比度优化：**
- 标题和重要文字使用更亮的白色
- 次要文字使用中等对比度灰色

## 实施步骤

### 步骤 1：修复状态栏显示
1. 检查 `table_view.py` 中 `_apply_search_filter` 方法
2. 确认调用 `update_search_status` 的逻辑
3. 测试搜索后状态栏更新

### 步骤 2：更新配色方案
1. 修改 `styles.py` 中的 `COLORS` 字典
2. 调整 Treeview 的行颜色
3. 优化对比度和可读性
4. 测试新配色在不同组件上的效果

## 影响范围
- `src/gui/table_view.py` - 搜索逻辑
- `src/gui/main_window.py` - 状态更新
- `src/gui/styles.py` - 全局配色

## 预期结果
1. 搜索后状态栏正确显示：`Records: 50 / 1000 (filtered)`
2. 界面配色更明亮，对比度更好，减少眼睛疲劳
3. 保持深色主题风格，但提高可读性
