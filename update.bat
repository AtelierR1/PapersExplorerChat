@echo off
@REM python�̎��s�p�X���w�肵�Ă��������B
set PYTHON_EXEC_PATH=python\path\python
echo "ragdata\input��csv�t�@�C�����i�[���Ă�������"
echo "csv�̕ύX�������ƃG���[��f���\��������̂ŁA1�x�ɕύX���鍀�ڂ�100�����x�ɂ��Ă�������"
pause
if not exist .\ragdata\update_output\*.parquet  (
    call %PYTHON_EXEC_PATH% -m graphrag index --config ./ragdata/settings.yaml --root ./ragdata
) else (
    call %PYTHON_EXEC_PATH% -m graphrag update --config ./ragdata/settings.yaml --root ./ragdata
    xcopy \Y .\ragdata\update_output\*.parquet .\ragdata\output
)
echo "Finish"
pause