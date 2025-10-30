@echo off
:: Auto Git Update Script
echo ============================
echo 🚀 Smartcard Git Auto Pusher
echo ============================
echo.

:: Step 1 - Add changes
git add .
echo ✅ All changes staged.

:: Step 2 - Commit changes
set /p msg=💬 Commit message লিখুন: 
if "%msg%"=="" set msg=Auto commit
git commit -m "%msg%"
echo ✅ Commit done.

:: Step 3 - Push to GitHub
git push origin main
echo ✅ Push complete.

echo.
echo 🎉 সবকিছু সফলভাবে GitHub এ পাঠানো হয়েছে!
pause
