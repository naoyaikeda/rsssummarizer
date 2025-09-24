# プロジェクト概要

このプロジェクトは、FreshRSS インスタンスから指定された期間内の未読RSSフィードアイテムを取得し、それらのタイトルを Google Gemini API を使用して要約するPythonスクリプトです。FreshRSSSummarizerプロジェクトから派生し、testclient.pyをベースにPyInstallerへの対応などを行っています。

# 技術スタック
- python
- uv
- langchain

# ファイル構成

- '[RSSInfra/](RSSInfra/)': RSSを用いるインフラストラクチャコード
- '[rsssummarizer.py](rsssummarizer.py)': rsssummarizerのメインコード
- '[MAKEFILE](MAKEFILE)': PyInstallerで実行物を生成するMAKEFILE
- '[pyproject.toml](pyproject.toml)': uvのプロジェクト
- '[README.md](README.md)': ドキュメント
- '[CHANGELOG.md](CHANGELOG.md)': 変更履歴
- '[VERSION](VERSION)': バージョン情報
- '[license.txt](license.txt)': ライセンス
- '[rsssummarizer.env](rsssummarizer.env)': 環境変数設定ファイル
