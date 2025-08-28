# プロジェクト概要

このプロジェクトは、FreshRSS インスタンスから指定された期間内の未読RSSフィードアイテムを取得し、それらのタイトルを Google Gemini API を使用して要約するPythonスクリプトです。FreshRSSSummarizerプロジェクトから派生し、testclient.pyをベースにPyInstallerへの対応などを行っています。

# 技術スタック
- python
- uv
- langchain

# ファイル構成

- 'RSSInfra/': RSSを用いるインフラストラクチャコード
- 'rsssummarizer.py': rsssummarizerのメインコード
- 'MAKEFILE': PyInstallerで実行物を生成するMAKEFILE
- 'pyproject.toml': uvのプロジェクト 
- 'README.md': ドキュメント
