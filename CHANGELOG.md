# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2025-10-03

### Added

- さくらインターネットの生成AI API (`sakura`) を使用した要約機能を追加。
- `.env` ファイルで `SUMMARIZE_METHOD` を `sakura` に設定することで利用可能。

### Changed

- `README.md` を全面的に見直し、最新の機能に合わせて内容を更新。
  - `sakura` 要約機能に関する説明を追加。
  - コマンドライン引数 (`--clip_name`, `--clip_title`, `--tags`) の説明を追記。
  - `.env` ファイルの設定例を更新。
  - キャッシュの更新条件に `summarize_method` を含めることを明記。
- ファイル構成のタイポを修正。

## [0.4.2] - 2025-09-23

### Changed

- Gemini APIに引き渡すデータにリンクを付加

## [0.4.1] - 2025-09-23

### Changed

- Geminiに渡すリストにリンクを追加
- READMEとファイルリストの同期

## [0.4.0] - 2025-09-21

### Changed

- フェッチアルゴリズムの変更

## [0.3.0] - 2025-09-18

### Added

- クリッピングファイルにメタ情報を追加

## [0.2.0] - 2025-09-17

### Added

- 要約結果をMarkdownファイルとして保存するクリッピング機能を追加。
- `--clip`, `--clip_dir`, `--clip_name` コマンドラインオプションを追加。
- `CLIP_DIR`, `CLIP_NAME` 環境変数をサポート。
- クリップされたMarkdownファイルにYAML frontmatterを追加。
- `--clip_title` オプションを追加し、Markdownのタイトルを生成できるようにした。
- `--tags` オプションを追加し、frontmatterのタグをカスタマイズできるようにした。

## [0.1.2] - 2025-09-07

### Fixed

- ファイル構成の更新、空のrsssummarizer.envを含めた。

## [0.1.1] - 2025-09-03

### Fixed

- PyInstallerでビルドした実行ファイルを実行した際に、`.env`ファイルが存在しないことによる警告が表示される問題を修正しました。
