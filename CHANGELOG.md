# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
