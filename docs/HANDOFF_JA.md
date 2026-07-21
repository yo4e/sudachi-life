# SUDACHI 再開用ハンドオフ

最終更新：2026年7月21日

## 現在地

SUDACHIのリポジトリを作成し、設計思想、起源、ロードマップ、初期アーキテクチャ、最小生命契約v0.1の初稿を記録した段階。

まだ実装コードはない。これは意図的な状態である。次は契約に残した設計上の未決事項を短いdecision recordで確定し、その後にSUDACHI-0のPython骨格へ入る。

## すでに決まっていること

- プロジェクト名：SUDACHI
- リポジトリ：`yo4e/sudachi-life`
- 最初の個体名：暫定 `SUDACHI-0`
- 主目的：親モデルの助力を、記憶・技能・決定論的な行動へ変換し、成長するほど親モデル依存を減らす
- 技術の初期候補：Python、SQLite、JSONL、Git、pytest
- 実行方式：常駐無限ループではなく、一回ごとに有限の周期を実行して終了する
- 最初はローカル、ネットワークアクセスなし
- Phase 1では親モデルを呼ばない
- 親接続の配線確認には、後で決定論的なmocked parentを使う
- リポジトリ全体を身体・発達履歴として扱う
- LLMは生命全体ではなく、必要時に利用する器官または親
- 成熟は「大きくなること」ではなく「親なしで保てる能力と時間が増えること」
- SUDACHI-0自身には、最初からソースコード自己改変を許可しない

## 言語方針

- README、コード、識別子、API、テスト、外向け技術文書：英語
- 起源、思想的なニュアンス、会話由来の文脈、再開メモ：日本語
- 重要な決定は、必要なら両言語で残す

英語だけにすると概念の出生地が失われ、日本語だけにすると外部との接続性が落ちるため、二層構造にした。

## このリポジトリを再開するときの読み順

1. `README.md`
2. `docs/ORIGIN_JA.md`
3. `docs/MINIMAL_ORGANISM_CONTRACT.md`
4. `docs/ROADMAP.md`
5. `docs/ARCHITECTURE.md`
6. `AGENTS.md`
7. このファイル

## 次に行う一件

**Minimal Organism Contract v0.1の未決事項を確定する。**

`docs/decisions/`を作り、少なくとも以下を短いADRとして決める。

1. `0001-state-and-event-storage.md`
   - SQLiteのみか、SQLite＋JSONL exportか
2. `0002-clock-and-determinism.md`
   - 実時刻と注入可能なclock interfaceの扱い
3. `0003-runtime-locking.md`
   - 同一個体の二重起動を防ぐ方式
4. `0004-checkpoints.md`
   - checkpointの表現とrollback単位
5. `0005-seed-environment.md`
   - 最初のsynthetic environmentとobjective
6. `0006-budget-metaphor.md`
   - energyを独立変数にするか、具体的budgetの表示に留めるか

俺の暫定推奨は次のとおり。

- 永続状態：SQLiteを正本にする
- event：SQLite内のappend-only tableを正本にし、JSONLは観察・実験用exportにする
- clock：実運用ではreal clock、テストでは注入可能なfake clock
- locking：最初はOS依存を減らすため、SQLiteのtransaction＋runtime lock recordから検討する
- checkpoint：SQLite backupまたは状態snapshot＋event offset
- seed environment：小さな仮想庭。数個のobjectとeventだけを持ち、action結果が決定論的に測れるもの
- energy：最初は別の神秘的な値にせず、具体的budgetの読みやすい表示として扱う

ADR確定後、`pyproject.toml`、`src/sudachi_life/`、`tests/`を作る。

## 最初の実装候補

最小CLI例：

```text
sudachi init
sudachi enqueue synthetic:file_changed
sudachi wake --seed 1
sudachi status
```

最初の一周期：

```text
wake
  ↓
stateを検証
  ↓
synthetic eventを1件読む
  ↓
決定論的なactionを1件選ぶ
  ↓
予算を消費
  ↓
結果を評価
  ↓
stateとevent logを保存
  ↓
checkpoint
  ↓
sleepしてプロセス終了
```

親モデルはまだ呼ばない。

## 初期の固定テスト

`docs/MINIMAL_ORGANISM_CONTRACT.md`のPhase 1 evaluationsを正とする。中心項目は次のとおり。

- 同じseed、state、event、configなら同じ結果になる
- 最大step数とtimeoutを超えない
- 許可外のファイルへ書き込めない
- 失敗してもdurable stateが破損しない
- event historyは追記のみ
- budgetが負にならない
- protected設定をactionから変更できない
- rollbackで直前の安定checkpointへ戻れる
- 二重起動を拒否できる
- abstentionとbudget exhaustionを明示的に記録する
- ネットワークも親モデルも必要としない

## やらないこと

現段階では、以下を先走って実装しない。

- 自由なインターネット探索
- 常時起動
- 無制限の自己改変
- 毎回のLoRA学習
- 大規模ベクトルDB
- 複数エージェント社会
- 物理ロボット
- リポジトリ外への自己複製
- 人格らしい会話演出を、生命機構より先に作ること

## 研究上の中心指標

最重要なのは、単一の賢さスコアではなく、次の変化を見ること。

- 1成功あたりの親呼び出し回数
- 親1回あたりに獲得した再利用可能な行動数
- 親なしで成功周期を続けられる時間
- 技能の再利用率
- 既存技能の組み合わせによる未知課題への転移
- 故障後の回復率
- 保持能力あたりの保存容量と推論コスト
- わからないときに正しく棄権できる率

## 次の俺へ

このプロジェクトを、一般的な「自律型AIエージェント」へ丸めないこと。

中心はタスク達成ではなく、発達である。

親に聞いた知恵が身体へ沈み、聞かなくてもできることが増え、記憶と技能が整理され、有限の身体で翌日へ続く。その過程を観測可能にすることがSUDACHIの本体である。

Minimal Organism Contractは初稿済み。次は未決事項をADRで閉じてから、最小CLIと一周期を実装する。

そして大きくしすぎるな。

**賢くなるほど、小さく、静かになる。**