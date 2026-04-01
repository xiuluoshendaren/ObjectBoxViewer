# 修复 GitHub Actions macOS Intel 构建错误

## 问题描述
GitHub Actions 构建 macOS Intel 版本时报错：
"The configuration 'macos-13-us-default' is not supported"

## 根本原因
GitHub Actions 的 macOS runner 配置可能已经更新。根据错误信息，`macos-13` 的某些配置不再支持。

## 解决方案
根据 GitHub Actions 最新文档，macOS Intel 构建应该使用：
- `macos-13` - 标准的 Intel runner
- 但可能需要显式指定 runner 的其他配置

实际上，GitHub 现在推荐：
- `macos-latest` - 当前指向 macOS 14 (M1/ARM64)
- `macos-14` - macOS 14 (M1/ARM64)
- `macos-13` - macOS 13 (Intel x86_64)
- `macos-12` - macOS 12 (Intel x86_64)

错误可能是因为：
1. GitHub 的基础设施变更
2. 需要使用不同的标签或配置

最佳解决方案是：
- 保持使用 `macos-13`，但确保没有其他配置冲突
- 或者降级到 `macos-12` 如果 13 有问题

## 修改步骤
1. 将 `build-macos-intel` job 的 `runs-on` 从 `macos-13` 改为 `macos-12` 或确认正确的配置
2. 测试构建是否成功

## 影响范围
- `.github/workflows/build.yml` 文件
- 仅影响 macOS Intel 构建流程
- 不影响 ARM64 和 Windows 构建
