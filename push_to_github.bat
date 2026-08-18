@echo off
setlocal
cd /d "%~dp0"

echo ==================================================================
echo  AWS 단가 게시판 - GitHub 업로드
echo  폴더: %CD%
echo ==================================================================
echo.

where git >nul 2>&1
if errorlevel 1 goto nogit
git --version

echo.
git config --global user.name >nul 2>&1
if errorlevel 1 goto askcfg
git config --global user.email >nul 2>&1
if errorlevel 1 goto askcfg
goto askrepo

:askcfg
echo [설정] 커밋에 기록할 이름과 이메일을 입력하세요. 최초 1회만 물어봅니다.
set /p GN="  이름: "
set /p GE="  이메일: "
git config --global user.name "%GN%"
git config --global user.email "%GE%"

:askrepo
echo.
echo [입력] GitHub 리포지토리 주소를 붙여넣으세요.
echo        리포 페이지의 초록색 Code 버튼에서 HTTPS 주소를 복사하면 됩니다.
echo        형식 예시: https://github.com/limsome/aws-price-board.git
set /p REPO="  주소: "
if "%REPO%"=="" goto norepo

echo.
echo [1/5] git init
if exist ".git" goto skipinit
git init
if errorlevel 1 goto fail
goto addall

:skipinit
echo       이미 초기화되어 있습니다. 건너뜁니다.

:addall
echo [2/5] git add .
git add .
if errorlevel 1 goto fail

echo [3/5] git commit
git diff --cached --quiet
if not errorlevel 1 goto nochange
git commit -m "AWS 단가 게시판 업데이트"
if errorlevel 1 goto fail
goto setremote

:nochange
echo       변경 사항이 없습니다. 건너뜁니다.

:setremote
echo [4/5] 브랜치 main 설정 및 원격 등록
git branch -M main
git remote get-url origin >nul 2>&1
if errorlevel 1 goto addremote
git remote set-url origin "%REPO%"
goto dopush

:addremote
git remote add origin "%REPO%"
if errorlevel 1 goto fail

:dopush
echo [5/5] git push
echo       브라우저 로그인 창이 뜨면 GitHub 계정으로 로그인하세요.
git push -u origin main
if errorlevel 1 goto fail

echo.
echo ==================================================================
echo  업로드 완료
echo.
echo  이제 GitHub 웹에서 두 가지를 설정하세요.
echo.
echo   1) Settings - Pages - Build and deployment - Source 를
echo      "GitHub Actions" 로 변경
echo   2) Settings - Actions - General - Workflow permissions 를
echo      "Read and write permissions" 로 변경 후 Save
echo.
echo  그 다음 Actions 탭에서 Update AWS prices 를 선택하고
echo  Run workflow 를 실행하세요. 3~6분 걸립니다.
echo.
echo  완료되면 접속 주소는 다음과 같습니다.
echo    https://[계정].github.io/aws-price-board/
echo ==================================================================
echo.
pause
exit /b 0

:nogit
echo [오류] git 을 찾을 수 없습니다.
echo        https://git-scm.com/download/win 에서 설치한 뒤
echo        명령 프롬프트를 새로 열고 다시 실행하세요.
echo.
pause
exit /b 1

:norepo
echo [오류] 주소가 입력되지 않았습니다.
echo.
pause
exit /b 1

:fail
echo.
echo ==================================================================
echo  실패했습니다. 위의 마지막 오류 메시지를 확인하세요.
echo.
echo  자주 나오는 원인
echo.
echo   Authentication failed
echo     비밀번호 대신 Personal Access Token 이 필요합니다.
echo     Settings - Developer settings - Personal access tokens
echo     - Tokens classic - Generate new token
echo     - repo 와 workflow 권한을 체크하고 생성한 뒤
echo     비밀번호 입력 자리에 붙여넣으세요.
echo.
echo   refusing to merge unrelated histories
echo     리포지토리 생성 시 README 를 추가한 경우입니다.
echo     git pull --rebase origin main 을 실행한 뒤 다시 시도하세요.
echo.
echo   repository not found
echo     주소 오타이거나 해당 리포에 접근 권한이 없습니다.
echo ==================================================================
echo.
pause
exit /b 1
