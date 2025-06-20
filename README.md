# rsssummarizer

## 概要

このプロジェクトは、[FreshRSS](https://freshrss.org/) インスタンスから指定された期間内の未読RSSフィードアイテムを取得し、それらのタイトルを [Google Gemini API](https://ai.google.dev/) を使用して要約するPythonスクリプトです。FreshRSSSummarizerプロジェクトから派生し、testclient.pyをベースにPyInstallerへの対応などを行っています。

## 主な機能

* FreshRSS API (Google Reader API互換) を介してFreshRSSインスタンスに接続します。
* 未読のRSSアイテムを取得します。
* 指定された時間範囲（例：過去24時間）に基づいてアイテムをフィルタリングします。
* フィルタリングされたアイテムのタイトルリストを生成します。
* Google Gemini API を使用して、タイトルリストの要約を生成します。
* 設定は環境変数とコマンドライン引数を通じて行います。

## 要件

* Python 3.x
* 以下のPythonライブラリ:
    * `freshrss-api`
    * `google-generativeai`
    * `python-dotenv`
* アクセス可能な FreshRSS インスタンス
* Google Gemini API キー

## インストール

1.  **リポジトリをクローン (またはファイルをダウンロード):**
    ```bash
    git clone <your-repository-url>
    cd <repository-directory>
    ```

2.  **必要なライブラリをインストール:**
    ```bash
    uv sync
    ```

## 設定

1.  プロジェクトのルートディレクトリに `.env` という名前のファイルを作成します。
2.  `.env` ファイルに以下の情報を記述します:

    ```dotenv
    # .env ファイルの例

    # FreshRSS インスタンスの GReader API エンドポイントURL
    # 例: [https://your.freshrss.domain/api/greader.php](https://your.freshrss.domain/api/greader.php)
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
python rsssummarizer.py
```

オプション:

    --delta_hours <時間数>: 何時間前までの未読アイテムを要約対象とするかを指定します。デフォルトは 24 時間です。
    Bash

        # 過去48時間分の未読アイテムを要約する場合
        python rsssummarizer.py --delta_hours 48

スクリプトは指定された期間の未読アイテムタイトルを取得し、Geminiによって生成された要約をコンソールに出力します。
ファイル構成 (例)

rsssummarizer/
│
├── RSSInfra
│    ├── Fetchers
│    │   ├── freshfeed_client.py
│    ├── Fetchers
│         ├── freshfeed_client.py
├── rsssummarizer.py           # クライアント/実行スクリプト
├── .env                    # 環境変数ファイル (Git管理外にすること)
├── pyproject.toml          #
└── README.md               # このファイル

ライセンス

Copyright (c) 2025, Naoya Ikeda

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
