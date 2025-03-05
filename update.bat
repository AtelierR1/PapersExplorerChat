@echo off
@REM pythonの実行パスを指定してください。
set PYTHON_EXEC_PATH=python\path\python
echo "ragdata\inputにcsvファイルを格納してください"
echo "csvの変更が多いとエラーを吐く可能性があるので、1度に変更する項目は100件程度にしてください"
pause
if not exist .\ragdata\update_output\*.parquet  (
    call %PYTHON_EXEC_PATH% -m graphrag index --config ./ragdata/settings.yaml --root ./ragdata
) else (
    call %PYTHON_EXEC_PATH% -m graphrag update --config ./ragdata/settings.yaml --root ./ragdata
    xcopy \Y .\ragdata\update_output\*.parquet .\ragdata\output
)
echo "Finish"
pause