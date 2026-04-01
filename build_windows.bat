@echo off
REM Build ObjectBox Viewer for Windows

echo =========================================
echo Building ObjectBox Viewer for Windows
echo =========================================

REM Check PyInstaller
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo Error: PyInstaller not found
    echo Please install it: pip install pyinstaller
    exit /b 1
)

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build for Windows
echo Building for Windows...
pyinstaller --clean --noconfirm ObjectBoxViewer.spec

REM Check if build succeeded
if exist "dist\ObjectBoxViewer\ObjectBoxViewer.exe" (
    echo ✅ Build successful!
    echo 📦 Output: dist\ObjectBoxViewer\

    REM Get directory size
    for /f %%A in ('dir /s "dist\ObjectBoxViewer" ^| find "File(s)"') do set size=%%A
    echo 📊 App size: %size% bytes
) else (
    echo ❌ Build failed!
    exit /b 1
)

echo =========================================
echo Build complete!
echo =========================================
pause
