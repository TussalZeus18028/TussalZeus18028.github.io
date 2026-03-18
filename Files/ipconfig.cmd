@echo off
setlocal enabledelayedexpansion

title 局域网 IP/MAC 扫描器（并行版）
echo ============================================
echo   局域网在线设备扫描（IP + MAC）
echo ============================================
echo.

:: 清理旧临时文件
del online_ips.txt 2>nul
del arp_results.txt 2>nul
del final_output.txt 2>nul

:: ---------- 1. 获取网段 ----------
echo 正在检测本机 IP 地址...
set "net="
set "local_ip="

:: 尝试从 ipconfig 获取第一个有效的 IPv4 地址（支持中/英文）
for /f "tokens=3 delims=: " %%i in ('ipconfig ^| findstr /c:"IPv4" /c:"IPv4 地址"') do (
    set "local_ip=%%i"
    goto :got_ip
)
:got_ip
if "%local_ip%"=="" (
    echo 无法自动获取 IP，请手动输入网段（例如 192.168.1）：
    set /p "net=网段（前三段）: "
) else (
    echo 本机 IP: %local_ip%
    for /f "tokens=1-3 delims=." %%a in ("%local_ip%") do set "net=%%a.%%b.%%c"
    echo 当前网段: %net%.x
)
echo.

:: 验证网段格式
if "%net%"=="" (
    echo 错误：网段不能为空，脚本退出。
    pause
    exit /b 1
)
echo %net% | findstr /r "^[0-9]*\.[0-9]*\.[0-9]*$" >nul
if errorlevel 1 (
    echo 错误：网段格式不正确，应为类似 192.168.1
    pause
    exit /b 1
)

:: ---------- 2. 并行 Ping 扫描 ----------
echo 正在并行扫描网段 %net%.1 到 %net%.254 ...
echo 请稍候（约 5-10 秒）...

:: 清空在线 IP 文件
type nul > online_ips.txt

:: 启动 254 个后台 Ping 进程（并发）
for /l %%i in (1,1,254) do (
    start /b cmd /c "ping -n 1 -w 100 %net%.%%i >nul 2>&1 && echo %net%.%%i >> online_ips.txt"
)

:: ---------- 3. 等待所有 Ping 结束 ----------
:wait_loop
set "ping_count=0"
for /f %%i in ('tasklist ^| find /c "ping.exe" 2^>nul') do set ping_count=%%i
if %ping_count% gtr 0 (
    timeout /t 1 /nobreak >nul
    goto wait_loop
)

echo 扫描完成。
echo.

:: ---------- 4. 检查是否发现在线设备 ----------
if not exist online_ips.txt (
    echo 错误：在线 IP 列表文件未生成。
    pause
    exit /b 1
)

for %%? in (online_ips.txt) do ( set file_size=%%~z? )
if "%file_size%"=="0" (
    echo 未发现任何在线设备，请检查网络或防火墙设置。
    pause
    exit /b 0
)

:: ---------- 5. 解析 MAC 地址 ----------
echo 正在获取 MAC 地址...
echo IP 地址                 MAC 地址 > final_output.txt
echo ------------------------------------ >> final_output.txt

:: 读取在线 IP 列表，逐个获取 MAC
for /f "usebackq delims=" %%a in ("online_ips.txt") do (
    set "ip=%%a"
    :: 先 Ping 一次，确保 ARP 缓存中有记录
    ping -n 1 -w 50 !ip! >nul 2>&1
    :: 从 ARP 表中提取 MAC
    for /f "tokens=1,2" %%b in ('arp -a !ip! ^| find "!ip!"') do (
        set "mac=%%c"
        :: 兼容不同 arp 输出格式（有时 MAC 在第二列）
        if "!mac!"=="" set "mac=%%b"
        echo !ip!             !mac! >> final_output.txt
        goto :next_ip
    )
    :: 如果没找到 MAC，记录“无法获取”
    echo !ip!             无法获取 >> final_output.txt
    :next_ip
)

:: ---------- 6. 显示结果 ----------
echo.
echo 扫描结果（已保存到 final_output.txt）：
echo ====================================
type final_output.txt
echo ====================================

:: 清理临时文件（保留 final_output.txt）
del online_ips.txt 2>nul
del arp_results.txt 2>nul

echo.
echo 按任意键退出...
pause >nul
endlocal