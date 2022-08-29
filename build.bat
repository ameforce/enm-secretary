set root=C:\Users\%USERNAME%\anaconda3
call %root%\Scripts\activate.bat %root%

taskkill /f /im ENM-Secretary.exe

call conda activate enm-secretary
call pyinstaller -n "ENM-Secretary" --onefile --noconsole main.py
call move "dist\ENM-Secretary.exe"

start "" "ENM-Secretary.exe"