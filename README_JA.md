# 🔍 Skill Discovery

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Skill-blue.svg)](https://code.anthropic.com)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)

> AIスキル、ツール、フレームワークを自動的に発見・追跡

[English](README_EN.md) | [日本語](README_JA.md) | [中文](README.md)

---

## ✨ 特徴

- 🤖 **自動検出** - AIが外部ツールの必要性を自動検出
- 🔍 **マルチソース検索** - GitHub、Reddit、Webを同時に検索
- 💾 **スマートキャッシュ** - 2段階キャッシュで即座に結果を表示
- 📊 **インテリジェントランキング** - 関連性に基づく推奨
- 🌍 **6つのプリセットドメイン** - ブラウザ自動化、AIエージェント、Python、DevOps、API、データ

---

## 🚀 クイックスタート

### インストール

```bash
# Claude skillsディレクトリにクローン
git clone https://github.com/ei060/skill-discovery.git ~/.claude/skills/skill-discovery

# Windowsの場合
git clone https://github.com/ei060/skill-discovery.git %USERPROFILE%\.claude\skills\skill-discovery
```

### 使用方法

Claudeと普段通り会話するだけ：

```
あなた: "Webサイトをスクレイピングしたい"
AI: [Skill Discoveryが自動起動]
AI: "Playwrightの方がSeleniumより良いことがわかりました..."
AI: [Playwrightを使用して実装]
```

---

## 📚 対応ドメイン

| ドメイン | キーワード | ソース | キャッシュTTL |
|----------|-----------|---------|--------------|
| ブラウザ自動化 | puppeteer, playwright, selenium | GitHub, Reddit, Web | 12時間 |
| AIエージェント | openclaw, claude, llm, autonomous | GitHub, Reddit, Web | 6時間 |
| Pythonスクリプト | python, automation, scripting | GitHub, Reddit | 12時間 |
| API統合 | api, rest, graphql, webhook | GitHub, Web | 12時間 |
| DevOpsツール | docker, kubernetes, cicd | GitHub, Reddit | 12時間 |
| データ分析 | pandas, jupyter, visualization | GitHub, Reddit | 12時間 |

---

## 🛠️ 仕組み

```
ユーザー入力
    ↓
1. ドメイン検出
   - キーワード: "automation", "deploy", "api"
   - コンテキスト分析
    ↓
2. キャッシュ確認
   - メモリキャッシュ（高速）
   - ファイルキャッシュ（永続）
   - TTL確認
    ↓
3. 並列検索
   - GitHub API（リポジトリ）
   - Reddit API（コミュニティ討議）
   - WebSearch（記事、チュートリアル）
    ↓
4. 統合 & ランキング
   - URL重複排除
   - 関連性スコアリング
   - 品質評価
    ↓
5. キャッシュ更新
    ↓
6. 結果表示
```

---

## 📦 プロジェクト構造

```
skill-discovery/
├── SKILL.md              # メインスキル定義
├── README.md             # このファイル
├── README_EN.md          # 英語版
├── README_JA.md          # 日本語版
├── USAGE_GUIDE.md        # 詳細使用ガイド
├── config/
│   ├── domains.json      # ドメイン設定
│   └── behavior.json     # 動作設定
├── scripts/
│   ├── search_github.py  # GitHub APIラッパー
│   ├── search_reddit.py  # Reddit APIフェッチャー
│   ├── merge_results.py  # 結果統合
│   └── update_cache.py   # キャッシュマネージャー
└── references/
    ├── domains.md        # ドメインドキュメント
    └── api_limits.md     # APIレート制限
```

---

## ⚙️ 設定

### 新規ドメイン追加

`config/domains.json`を編集：

```json
{
  "id": "new-domain",
  "name": "表示名",
  "enabled": true,
  "keywords": ["キーワード1", "キーワード2"],
  "github_query": "検索クエリ",
  "subreddits": ["関連サブレディット"],
  "sources": ["github", "reddit", "web"],
  "schedule": "weekly",
  "cache_ttl": 43200000,
  "priority": 5
}
```

---

## 🧪 テスト

```bash
# GitHub検索テスト
python scripts/search_github.py

# Reddit検索テスト
python scripts/search_reddit.py

# キャッシュ管理テスト
python scripts/update_cache.py
```

---

## 📈 パフォーマンス

- **メモリキャッシュ**: < 1ms
- **ファイルキャッシュ**: < 10ms
- **新規検索**: 2-5秒

---

## 🤝 コントリビューション

コントリビューションを歓迎します！お気軽にプルリクエストを提出してください。

---

## 📝 ライセンス

このプロジェクトはMITライセンスの下でライセンスされています - 詳しくは[LICENSE](LICENSE)ファイルを参照してください。

---

## 🙏 謝辞

- [Claude Code](https://code.anthropic.com/)のために構築
- [OpenClaw](https://github.com/openclaw/openclaw)スキルエコシステムにインスピアを受けています
- GitHub、Reddit、Web Search APIsを活用

---

## 📮 コンタクト

- **Issues**: [GitHub Issues](https://github.com/ei060/skill-discovery/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ei060/skill-discovery/discussions)

---

<div align="center">

**Made with ❤️ by [ei060](https://github.com/ei060)**

</div>
