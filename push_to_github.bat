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
git remote get-url origin >nul 2>&1
if errorlevel 1 goto needrepo
for /f "tokens=*" %%r in ('git remote get-url origin') do set REPO=%%r
echo [정보] 등록된 리포지토리: %REPO%
echo        그대로 쓰려면 엔터, 바꾸려면 새 주소를 입력하세요.
set /p NEWREPO="  주소 (엔터=유지): "
if not "%NEWREPO%"=="" set REPO=%NEWREPO%
goto haverepo

:needrepo
echo [입력] GitHub 리포지토리 주소를 붙여넣으세요.
echo        리포 페이지의 초록색 Code 버튼에서 HTTPS 주소를 복사하면 됩니다.
echo        형식 예시: https://github.com/limsome/aws-price-board.git
set /p REPO="  주소: "
if "%REPO%"=="" goto norepo

:haverepo
echo.
echo [1/6] git init
if exist ".git" goto skipinit
git init
if errorlevel 1 goto fail
goto addall

:skipinit
echo       이미 초기화되어 있습니다. 건너뜁니다.

:addall
echo [2/6] git add .
git add .
if errorlevel 1 goto fail

echo [3/6] git commit
git diff --cached --quiet
if not errorlevel 1 goto nochange
git commit -m "AWS 단가 게시판 업데이트"
if errorlevel 1 goto fail
goto setremote

:nochange
echo       새로 담을 변경 사항이 없습니다. 건너뜁니다.

:setremote
echo [4/6] 브랜치 main 설정 및 원격 등록
git branch -M main
git remote get-url origin >nul 2>&1
if errorlevel 1 goto addremote
git remote set-url origin "%REPO%"
goto sync

:addremote
git remote add origin "%REPO%"
if errorlevel 1 goto fail

:sync
echo [5/6] 원격 변경 사항 가져오기
echo       (자동 갱신 워크플로우가 만든 커밋을 먼저 합칩니다)
git fetch origin main >nul 2>&1
if errorlevel 1 goto firstpush
git rev-parse --verify origin/main >nul 2>&1
if errorlevel 1 goto firstpush
git pull --rebase origin main
if errorlevel 1 goto conflict

:firstpush
echo [6/6] git push
echo       브라우저 로그인 창이 뜨면 GitHub 계정으로 로그인하세요.
git push -u origin main
if errorlevel 1 goto pushfail

echo.
echo ==================================================================
echo  업로드 완료
echo.
echo  사이트에 반영되기까지 1~6분 걸립니다.
echo  Actions 탭에서 진행 상황을 볼 수 있습니다.
echo.
echo  접속 주소
echo    https://ku891005.github.io/aws-price-board/
echo ==================================================================
echo.
pause
exit /b 0

:conflict
echo.
echo ==================================================================
echo  같은 파일을 로컬과 원격에서 함께 수정해 충돌이 났습니다.
echo.
echo  원격(GitHub) 내용을 기준으로 맞추려면 아래를 실행하세요.
echo    git rebase --abort
echo    git reset --hard origin/main
echo  단, 이 경우 로컬에서만 수정한 내용은 사라집니다.
echo.
echo  판단이 어려우면 이 화면을 그대로 전달해 주세요.
echo ==================================================================
echo.
pause
exit /b 1

:pushfail
echo.
echo ==================================================================
echo  push 가 거부되었습니다.
echo.
echo  rejected / fetch first 가 보이면 원격에 새 커밋이 있다는 뜻입니다.
echo  이 배치 파일을 한 번 더 실행하면 자동으로 합친 뒤 다시 올립니다.
echo.
echo  Authentication failed 가 보이면 토큰이 필요합니다.
echo    Settings - Developer settings - Personal access tokens
echo    - Tokens classic - Generate new token
echo    - repo 와 workflow 권한 체크 후 생성
echo    - 비밀번호 입력 자리에 붙여넣기
echo ==================================================================
echo.
pause
exit /b 1

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
echo ==================================================================
echo.
pause
exit /b 1
