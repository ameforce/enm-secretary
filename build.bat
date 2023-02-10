@ECHO OFF

set root=C:\Users\%USERNAME%\anaconda3

echo | set /p="Trying to run conda..."
call %root%\Scripts\activate.bat %root%
echo Success !!

echo | set /p="Changing conda's environment..."
call conda activate enm-secretary 2> NUL

if errorlevel 1 (
  echo Failure
  echo The enm-secretary environment does not exist
  echo | set /p="Creating enm-secretary environment.."
  call conda create -n enm-secretary python=3.11 -y > NUL 2>&1
  echo | set /p="Creating enm-secretary environment..."
  call conda activate enm-secretary
)
echo Success !!

echo | set /p="Installing require python packages..."
call pip install -r requirements.txt > NUL
echo Success !!

echo | set /p="Shutting down the running ENM-Secretary.exe process..."
taskkill /f /im ENM-Secretary.exe > NUL 2>&1
echo Success !!

echo | set /p="Building main.py to ENM-Secretary.exe..."
call pyinstaller -n "ENM-Secretary" --onefile --noconsole main.py > NUL 2>&1
echo Success !!

echo | set /p="Moving ENM-Secretary.exe..."
call move "dist\ENM-Secretary.exe" > NUL
echo Success !!

echo | set /p="Running ENM-Secretary.exe..."
start "" "ENM-Secretary.exe"
echo Success !!


