# メタデータ生成仕様 (Metadata Generation Spec)

`src/lib/video/metadata.py` における、動画ファイルからのメタデータ（タイトル、説明、タグ、撮影情報）生成ルールについて記述します。

## 1. 概要

本ツールはユーザーの手入力を最小限にするため、**テンプレート設定** と **ファイルシステムの情報（パス、ファイル名）** と **動画ファイルの内部メタデータ（撮影日時）** を組み合わせて、YouTube アップロード用の情報を自動生成します。

## 2. テンプレート設定

### 2.1 グローバル設定 (`settings.yaml`)

`metadata` セクションでテンプレートを設定します。

```yaml
metadata:
  title_template: "【{folder}】{stem}"
  description_template: |
    {folder}
    No. {index}/{total}

    File: {filename}
    Captured: {date}
  tags:
    - "auto-upload"
```

### 2.2 フォルダ別オーバーライド (`.yt-meta.yaml`)

動画フォルダに `.yt-meta.yaml` を配置すると、そのフォルダの動画だけテンプレートを上書きできます。

```yaml
# .yt-meta.yaml の例
title_template: "{stem} @ {folder}"
description_template: "Custom description for {filename}"
tags: ["custom-tag"]           # タグを完全に置き換え
extra_tags: ["vacation", "beach"]  # 既存タグに追加
```

### 2.3 利用可能なテンプレート変数

| 変数 | 説明 | 例 |
|---|---|---|
| `{folder}` | 親フォルダ名 | `Vlog2023` |
| `{stem}` | ファイル名（拡張子なし） | `Beach` |
| `{filename}` | ファイル名（拡張子あり） | `Beach.mp4` |
| `{date}` | 撮影日時（`YYYY-MM-DD HH:MM:SS`、不明時は `Unknown`） | `2023-08-15 14:30:00` |
| `{year}` | 撮影年（不明時は空文字） | `2023` |
| `{index}` | 現在のファイルインデックス | `1` |
| `{total}` | 総ファイル数 | `10` |

## 3. 生成ルール

### 3.1 タイトル (Title)

- **デフォルトフォーマット**: `【{folder}】{stem}`
- **制約**: YouTube のタイトル制限（全角・半角問わず 100 文字）に収まるよう、超過する場合は末尾をトリミングして `...` を付与します。
- **例**:
  - パス: `Travel/Vlog2023/Beach.mp4`
  - **生成タイトル**: `【Vlog2023】Beach`

### 3.2 説明文 (Description)

- **デフォルトフォーマット**:
  ```text
  {folder}
  No. {index}/{total}

  File: {filename}
  Captured: {date}
  ```

### 3.3 タグ (Tags)

- **ベースタグ**: `settings.yaml` の `metadata.tags` で定義（デフォルト: `["auto-upload"]`）
- **動的タグ**: フォルダ名と撮影年が自動追加される
- **フォルダ別タグ**: `.yt-meta.yaml` の `tags`（完全置換）または `extra_tags`（追加）で制御
- **例**: `["auto-upload", "Vlog2023", "2023"]`

### 3.4 撮影日時 (Recording Details)

- **取得元**: ファイル内部のメタデータ（`hachoir` ライブラリを使用し、`creation_date` を解析）。
- **API フィールド**: `recordingDetails.recordingDate`
- **フォーマット**: `YYYY-MM-DDThh:mm:ss.sZ` (ISO 8601 UTC)
- **場所 (Location)**: ファイルからGPS情報（緯度・経度・高度）が取得可能な場合、`recordingDetails.location` に設定されます。MOVファイルでは `hachoir` で取得できない場合にバイナリスキャン (ISO 6709) でフォールバックします。
- **注意**: ファイルメタデータが存在しない、または解析不能な場合は設定されません。

## 4. 実装詳細

`src.lib.video.metadata.FileMetadataGenerator` クラスがこの責務を担います。
- テンプレート展開には `str.format_map()` を使用（外部依存なし）
- `.yt-meta.yaml` は `_load_folder_override()` で読み込み、 `_resolve_template_config()` でマージ
- 不正なテンプレート変数がある場合はデフォルトにフォールバック
- `hachoir` パーサーを使用し、エラー時はデフォルト値（日付なし等）にフォールバック
