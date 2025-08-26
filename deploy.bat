@echo off
echo ========================================
echo  Deploying Muda-Mudi Authentication System
echo ========================================

echo.
echo 1. Installing dependencies...
call npm install

echo.
echo 2. Building project...
call npm run build

echo.
echo 3. Deploying to Vercel...
call vercel --prod

echo.
echo ========================================
echo  Deployment completed!
echo ========================================
echo.
echo Next steps:
echo 1. Update API_BASE_URL in auth/login_manager.py
echo 2. Update API_BASE_URL in public/admin.html
echo 3. Setup Supabase database with schema.sql
echo 4. Configure environment variables in Vercel
echo.
pause