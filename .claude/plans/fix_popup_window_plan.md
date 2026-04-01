# 修复提示窗口被遮挡问题

## 目标
修复详情视图中"Copy to Clipboard"按钮点击后，弹出提示窗口被主窗口遮挡的问题。

## 当前问题
- 点击"Copy to Clipboard"按钮后，弹出提示窗口
- 提示窗口被主窗口遮挡，看不到
- 用户无法及时收到操作反馈

## 问题分析

**文件：** `src/gui/detail_view.py`
**方法：** `_show_message`

**当前代码问题：**
```python
popup = ctk.CTkToplevel(self)
popup.title("Message" if not error else "Error")
popup.geometry("300x100")
```

问题：
1. 没有设置窗口居中
2. 没有设置 `topmost` 属性
3. 没有设置 `transient` 属性确保显示在父窗口之上

## 修改方案

### 1. 设置窗口属性
- `transient(self)` - 设置为父窗口的临时窗口
- `grab_set()` - 抓取焦点
- `topmost` - 确保显示在最顶层（可选）

### 2. 窗口居中显示
计算父窗口位置，将提示窗口居中显示：
```python
# 获取父窗口位置和大小
parent_x = self.winfo_x()
parent_y = self.winfo_y()
parent_width = self.winfo_width()
parent_height = self.winfo_height()

# 计算居中位置
popup_width = 300
popup_height = 100
x = parent_x + (parent_width - popup_width) // 2
y = parent_y + (parent_height - popup_height) // 2

popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")
```

### 3. 提升用户体验
- 添加 `transient(self)` 确保窗口层级关系
- 可选：添加 `grab_set()` 模态显示
- 设置焦点到确定按钮

## 实施步骤
1. 修改 `_show_message` 方法
2. 添加窗口居中计算逻辑
3. 设置正确的窗口属性
4. 测试提示窗口显示效果

## 影响范围
- `src/gui/detail_view.py` - 仅修改提示窗口显示逻辑

## 预期结果
- 提示窗口显示在父窗口正中间
- 提示窗口在最顶层，不被遮挡
- 用户能立即看到操作反馈
