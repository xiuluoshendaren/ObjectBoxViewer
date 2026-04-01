# 修复提示窗口显示问题

## 问题
"Copy to Clipboard" 按钮点击后，弹出的提示窗口被主窗口遮挡，应该在正中间最顶层显示。

## 原因分析
1. 提示窗口没有设置为父窗口的 transient
2. 没有设置窗口居中位置
3. 窗口层级管理不当

## 解决方案
1. 设置 popup 为 transient 到父窗口
2. 计算并设置窗口居中位置
3. 确保窗口在最顶层显示
4. 设置 grab 确保模态显示

## 修改位置
- `src/gui/detail_view.py` 的 `_show_message` 方法
