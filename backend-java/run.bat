@echo off
echo ========================================
echo Penguin-Land Java Backend 시작
echo ========================================
echo.

REM 환경 변수 체크
if "%AWS_ACCESS_KEY_ID%"=="" (
    echo [경고] AWS_ACCESS_KEY_ID가 설정되지 않았습니다!
    echo 환경 변수를 설정하거나 .env 파일을 만들어주세요.
    echo.
)

if "%AWS_SECRET_ACCESS_KEY%"=="" (
    echo [경고] AWS_SECRET_ACCESS_KEY가 설정되지 않았습니다!
    echo.
)

echo [정보] 서버를 시작합니다...
echo [정보] URL: http://localhost:8080
echo [정보] 중지: Ctrl+C
echo.
echo ========================================
echo.

REM Gradle 실행
gradlew.bat bootRun

pause
