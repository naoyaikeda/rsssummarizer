# rsssummarizer

## 概要

このプロジェクトは、[FreshRSS](https://freshrss.org/) インスタンスから指定された期間内の未読RSSフィードアイテムを取得し、それらのタイトルを [Google Gemini API](https://ai.google.dev/) を使用して要約するPythonスクリプトです。FreshRSSSummarizerプロジェクトから派生し、testclient.pyをベースにPyInstallerへの対応などを行っています。

## 主な機能

*   **FreshRSS連携**: FreshRSS API (Google Reader API互換) を介してインスタンスに接続し、未読のRSSアイテムを取得します。
*   **柔軟なフィルタリング**: 指定された時間範囲（例：過去24時間）に基づいてアイテムをフィルタリングします。
*   **Geminiによる要約**: Google Gemini API を活用し、取得した記事のタイトルリストから簡潔な要約を生成します。
*   **キャッシュ機能**: 一度生成した要約をキャッシュし、同じ条件での実行時にAPIの不要な再呼び出しを防ぎます。これにより、API使用量とコストを節約できます。
*   **カスタマイズ可能なプロンプト**: `--custom_prompt` 引数を使用することで、Geminiに与える指示（プロンプト）を自由に変更し、要約の形式や内容を調整できます。
*   **設定の容易さ**: 設定は `.env` ファイルとコマンドライン引数を通じて簡単に行えます。

## 要件

*   Python 3.10以上
*   アクセス可能な FreshRSS インスタンス
*   Google Gemini API キー

必要なPythonライブラリは `pyproject.toml` に記載されており、後述する `uv sync` コマンドで全てインストールされます。

## インストール

1.  **リポジトリをクローン (またはファイルをダウンロード):**
    ```bash
    git clone https://github.com/your-username/rsssummarizer.git
    cd rsssummarizer
    ```

2.  **仮想環境の作成と有効化:**
    ```bash
    uv venv
    source .venv/bin/activate  # macOS / Linux
    .venv\Scripts\activate    # Windows
    ```

3.  **必要なライブラリをインストール:**
    ```bash
    uv sync
    ```

## 設定

1.  プロジェクトのルートディレクトリに `.env` という名前のファイルを作成します。
2.  `.env` ファイルに以下の情報を記述します:

    ```dotenv
    # .env ファイルの例

    # FreshRSS インスタンスの GReader API エンドポイントURL
    # 例: https://your.freshrss.domain/api/greader.php
    HOST="<Your FreshRSS API Endpoint URL>"

    # FreshRSS ユーザー名
    USERNAME="<Your FreshRSS Username>"

    # FreshRSS API パスワード (注意: FreshRSSの設定 > プロフィール > API管理 で生成したパスワードを使用してください)
    PASSWORD="<Your FreshRSS API Password>"

    # Google Gemini API キー
    GEMINI_API_KEY="<Your Google Gemini API Key>"

    # (任意) 使用する Gemini モデル名 (デフォルトはコード内で指定されています)
    GEMINI_MODEL_NAME="gemini-1.5-flash" # 例: gemini-1.5-flash, gemini-pro など
    ```

    **重要:** FreshRSSのAPIパスワードは、通常のログインパスワードではなく、FreshRSSの設定画面で生成した専用のAPIパスワードを使用してください。

## 使用方法

以下のコマンドを実行してスクリプトを起動します。

```bash
python rsssummarizer.py [オプション]
```

### オプション

*   `--delta_hours <時間数>`: 何時間前までの未読アイテムを要約対象とするかを指定します。デフォルトは `24` 時間です。
*   `--max_items <アイテム数>`: 要約に使用するタイトルの最大数を指定します。デフォルトは `20` です。
*   `--custom_prompt <文字列>`: 要約生成時に使用するカスタムプロンプトを指定します。
*   `--log_level <レベル>`: ログレベルを `DEBUG` または `INFO` に設定します。デフォルトは `DEBUG` です。

### 使用例

```bash
# 過去48時間分の未読アイテムを要約する
python rsssummarizer.py --delta_hours 48

# 要約するアイテム数を10に制限し、特定のプロンプトを使用する
python rsssummarizer.py --max_items 10 --custom_prompt "箇条書きで出力してください。"
```

## キャッシュについて

このスクリプトは、生成した要約をキャッシュする機能を備えています。

*   **目的**: 同じパラメータ（期間、アイテム数、カスタムプロンプト）での実行時に、Gemini APIへの不要なリクエストを避け、応答を高速化するためです。
*   **場所**: キャッシュは、ユーザーのホームディレクトリ配下の `.rsssummarizer/rsssummarizer.db` に保存されます。
*   **更新タイミング**: 実行時の時刻（時単位）、`delta_hours`, `max_items`, `custom_prompt` のいずれかが前回の実行と異なる場合に、キャッシュは更新（再生成）されます。

## ファイル構成

```
.
├── .gitignore
├── .python-version
├── GEMINI.md
├── license.txt
├── MAKEFILE
├── pyproject.toml
├── CHANGELOG.md
├── README.md
├── rsssummarizer.py
├── RSSInfra/
│   ├── Article/
│   │   └── article.py
│   ├── Fetchers/
│   │   └── freshfeed_client.py
│   └── Summarizer/
│       └── gemini_summarizer.py
└── uv.lock
```

## ライセンス

このプロジェクトは [BSD 2-Clause "Simplified" License](./license.txt) の下で公開されています。
詳細は `license.txt` ファイルをご覧ください。