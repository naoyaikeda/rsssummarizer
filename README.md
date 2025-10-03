# rsssummarizer

## 概要

このプロジェクトは、[FreshRSS](https://freshrss.org/) インスタンスから指定された期間内の未読RSSフィードアイテムを取得し、それらのタイトルをLLMを使用して要約するPythonスクリプトです。要約には [Google Gemini API](https://ai.google.dev/) または [さくらインターネットの生成AI API](https://www.sakura.ad.jp/services/generative-ai/) を利用できます。

## 主な機能

*   **FreshRSS連携**: FreshRSS API (Google Reader API互換) を介してインスタンスに接続し、未読のRSSアイテムを取得します。
*   **柔軟なフィルタリング**: 指定された時間範囲（例：過去24時間）に基づいてアイテムをフィルタリングします。
*   **選べる要約エンジン**: Google Gemini または さくらの生成AI を選択して、記事のタイトルリストから簡潔な要約を生成します。
*   **キャッシュ機能**: 一度生成した要約をキャッシュし、同じ条件での実行時にAPIの不要な再呼び出しを防ぎます。これにより、API使用量とコストを節約できます。
*   **カスタマイズ可能なプロンプト**: `--custom_prompt` 引数を使用することで、LLMに与える指示（プロンプト）を自由に変更し、要約の形式や内容を調整できます。
*   **クリッピング機能**: 生成された要約をMarkdownファイルとして保存できます。ファイル名、タイトル、タグなどを細かく設定可能です。
*   **設定の容易さ**: 設定は `.env` ファイルとコマンドライン引数を通じて簡単に行えます。

## 要件

*   Python 3.10以上
*   アクセス可能な FreshRSS インスタンス
*   Google Gemini API キー または さくらインターネット生成AI APIキー

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

    # 要約メソッド ('gemini' または 'sakura')
    SUMMARIZE_METHOD="gemini"

    # 使用するLLMのAPIキー
    API_KEY="<Your API Key>"

    # (任意) 何時間前までの未読アイテムを要約対象とするか
    DELTA_HOURS=24

    # (任意) 要約に使用するタイトルの最大数
    MAX_ITEMS=20

    # (任意) 使用するモデル名 (デフォルトはコード内で指定)
    # gemini例: "gemini-1.5-flash", sakura例: "gpt-oss-120b"
    MODEL_NAME="gemini-1.5-flash"

    # (任意) カスタムプロンプト
    CUSTOM_PROMPT="<CUSTOM PROMPT>"
    
    # (任意) sakuraメソッド利用時、プロンプトが長すぎる場合に切り詰める文字数
    MAX_CHARS=300000

    # --- クリッピング設定 (任意) ---
    # クリップファイルを保存するディレクトリ
    CLIP_DIR="<CLIP DIR>"

    # クリップファイルの命名規則 (strftime形式)
    CLIP_NAME="%Y-%m-%d-%H.md"

    # クリップファイルのタイトル (strftime形式)
    CLIP_TITLE="Summary for %Y-%m-%d %H:00"
    ```

    **重要:** FreshRSSのAPIパスワードは、通常のログインパスワードではなく、FreshRSSの設定画面で生成した専用のAPIパスワードを使用してください。

## 使用方法

以下のコマンドを実行してスクリプトを起動します。

```bash
python rsssummarizer.py [オプション]
```

### オプション

*   `--delta_hours <時間数>`: 何時間前までの未読アイテムを要約対象とするか。デフォルトは `24`。
*   `--max_items <アイテム数>`: 要約に使用するタイトルの最大数。デフォルトは `20`。
*   `--custom_prompt <文字列>`: 要約生成時に使用するカスタムプロンプト。
*   `--log_level <レベル>`: ログレベルを `DEBUG` または `INFO` に設定。デフォルトは `DEBUG`。
*   `--clip`: このフラグを立てると、要約をMarkdownファイルとして保存します。
*   `--clip_dir <パス>`: クリップファイルを保存するディレクトリを指定します。
*   `--clip_name <パターン>`: クリップファイルの命名規則を `strftime` 形式で指定します。
*   `--clip_title <パターン>`: クリップファイルのタイトルを `strftime` 形式で指定します。
*   `--tags <タグ ...>`: クリップファイルのフロントマターに追加するタグをスペース区切りで指定します。デフォルトは `rss summary`。

### 使用例

```bash
# 過去48時間分の未読アイテムを要約する
python rsssummarizer.py --delta_hours 48

# 要約するアイテム数を10に制限し、カスタムプロンプトを使い、結果をクリップする
python rsssummarizer.py --max_items 10 --custom_prompt "箇条書きで出力してください。" --clip

# クリップファイルに 'work' と 'important' タグを追加する
python rsssummarizer.py --clip --tags work important
```

## キャッシュについて

このスクリプトは、生成した要約をキャッシュする機能を備えています。

*   **目的**: 同じパラメータでの実行時に、APIへの不要なリクエストを避け、応答を高速化するためです。
*   **場所**: キャッシュは、ユーザーのホームディレクトリ配下の `.rsssummarizer/rsssummarizer.db` に保存されます。
*   **更新タイミング**: 実行時の時刻（時単位）、`delta_hours`, `max_items`, `custom_prompt`, `summarize_method` のいずれかが前回の実行と異なる場合に、キャッシュは更新（再生成）されます。

## ファイル構成

```
.
├── CHANGELOG.md
├── GEMINI.md
├── MAKEFILE
├── README.md
├── RSSInfra
│   ├── Article
│   │   └── article.py
│   ├── Fetchers
│   │   └── freshfeed_client.py
│   └── Summarizer
│       ├── gemini_summarizer.py
│       └── sakura_summarizer.py
├── VERSION
├── license.txt
├── pyproject.toml
├── rsssummarizer.env
├── rsssummarizer.py
├── testcode.py
└── uv.lock
```

## ライセンス

このプロジェクトは [BSD 2-Clause "Simplified" License](./license.txt) の下で公開されています。
詳細は `license.txt` ファイルをご覧ください。
