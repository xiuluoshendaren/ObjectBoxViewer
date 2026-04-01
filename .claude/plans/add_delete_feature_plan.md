# 添加删除记录功能

## 目标
在详情视图中添加"删除记录"按钮，让用户可以删除选中的记录。

## 当前状态
- ✅ 后端删除逻辑已实现：`src/db.py` 的 `delete_record` 方法
- ❌ GUI 界面缺少删除按钮
- ❌ 删除操作需要确认对话框

## 问题分析

**文件：** `src/gui/detail_view.py`

**当前按钮：**
1. Copy to Clipboard - 复制到剪贴板
2. Export to JSON - 导出为 JSON
3. Close - 关闭窗口

**缺少：**
- Delete Record - 删除记录按钮

## 修改方案

### 1. 添加删除按钮
- 在详情视图底部添加"Delete Record"按钮
- 使用危险样式（红色）
- 位置：在 Close 按钮左边

### 2. 实现删除逻辑
```python
def _delete_record(self):
    # 1. 显示确认对话框
    # 2. 调用 db.delete_record()
    # 3. 显示删除结果
    # 4. 关闭详情窗口
    # 5. 刷新表格视图
```

### 3. 确认对话框
- 标题：Confirm Delete
- 内容：Are you sure you want to delete record #{record_id}? This action cannot be undone.
- 按钮：Delete / Cancel

### 4. 数据库打开模式
- 当前数据库以只读模式打开（`readonly=True`）
- 删除操作需要写权限
- 需要提示用户重新打开数据库为读写模式

## 实施步骤

### 步骤 1：修改详情视图
1. 添加删除按钮到 footer
2. 实现 `_delete_record` 方法
3. 添加确认对话框
4. 调用删除回调函数

### 步骤 2：修改主窗口
1. 添加删除记录回调
2. 接收 record_id 和 entity_id
3. 调用 db.delete_record()
4. 刷新表格数据

### 步骤 3：数据库打开模式
**选项 A（推荐）：** 在打开数据库时提示用户选择模式
- 只读模式（默认）
- 读写模式（允许删除）

**选项 B：** 删除时重新打开数据库为读写模式

## 影响范围
- `src/gui/detail_view.py` - 添加删除按钮和逻辑
- `src/gui/main_window.py` - 添加删除回调
- `src/db.py` - 可能需要修改打开模式

## 预期结果
- 详情视图显示"Delete Record"按钮
- 点击按钮显示确认对话框
- 确认后删除记录
- 表格自动刷新
- 显示删除成功/失败提示

## 安全考虑
- ✅ 必须显示确认对话框
- ✅ 确认对话框明确提示不可撤销
- ✅ 删除失败时显示错误信息
- ✅ 数据库只读时提示用户
