pyinstaller --noconsole -y -F --paths "%PYTHON_PATH%\Lib\site-packages\PyQt5\Qt\bin" Stage2TCX.py
move dist\Stage2TCX.exe .
