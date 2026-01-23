@echo off
chcp 65001 > nul
echo ========================================
echo 動画ダイエットくんを起動しています...
echo ========================================
echo.

REM 仮想環境が存在しない場合は作成
if not exist "venv" (
    echo 仮想環境を作成しています...
    python -m venv venv
)

REM 仮想環境を有効化
call venv\Scripts\activate.bat

REM 必要なライブラリをインストール
echo 必要なライブラリをインストールしています...
pip install -r requirements.txt --quiet

echo.
echo ブラウザが自動的に開きます...
echo 閉じる場合は Ctrl+C を押してください
echo.

REM Streamlitアプリを起動
streamlit run app_converter.py

pause


