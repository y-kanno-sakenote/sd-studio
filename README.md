# sd-studio — ローカル画像生成（Stable Diffusion / ComfyUI）

Mac mini M4 Pro（24GB, MPS）でローカル完結する画像生成環境。ネットにも課金にも依存しない。

## 構成
| 場所 | 中身 |
|---|---|
| `~/ComfyUI` | ComfyUI本体・venv（Python 3.12）・モデル。サードパーティなのでgit管理外 |
| `dev/sd-studio`（ここ） | 起動スクリプト・生成CLI・プロンプト集・出力。git管理 |

## 使い方
```bash
# 1. サーバ起動（起動しっぱなしにする。ブラウザGUIは http://127.0.0.1:8188）
dev/sd-studio/bin/start.sh

# 2. 別ターミナル or Claude から一括生成
python3 dev/sd-studio/gen.py "1girl, sake brewery, kimono" -n 4
python3 dev/sd-studio/gen.py "japanese sake bottle on wooden counter" -m photo
```

出力は `out/` に落ちる（gitignore済み）。

## モデル
| プリセット | ckpt | 用途 |
|---|---|---|
| `illust`（既定） | animagine-xl-4.0 | アニメ・イラスト。カード絵、キャラ、ゲーム素材 |
| `photo` | juggernautXL-v9 | 写実。酒瓶・料理・資料スライド用 |

VAE は `sdxl_vae.safetensors`（fp16-fix）を共通で使う。

## gen.py の主なオプション
- `-m illust|photo` モデル切替
- `-n 4` 枚数（バッチ）
- `-s 832x1216` 解像度（SDXLは総画素100万前後が最適。1024x1024 / 832x1216 / 1216x832）
- `--seed 12345` 固定シード（同じ絵を再現したいとき）
- `--steps` `--cfg` `--sampler` `--scheduler`
- `--negative "..."` ネガティブ上書き
- `--raw` 品質タグを足さずプロンプトをそのまま使う
- `--tag card` 出力ファイル名の接頭辞

## モデルを増やす
`~/ComfyUI/models/checkpoints/` に `.safetensors` を置くだけ。LoRAは `models/loras/`。
GUI の ComfyUI-Manager（導入済み）からノード・モデルを追加できる。

## 注意
- 初回生成はモデルロードで数分かかる。2回目以降は約61秒/枚（illust既定 steps=20・約100万画素）
- **MPSではバッチで速くならない**。`-n 4` は4枚出るが所要時間もほぼ4倍（実測87s/枚のまま）
- `1536x1536` は落ちないが人物が二重化して構図が壊れる。SDXLは1024px級に収めること
- GUIとCLIは同じサーバを共有する。GUIで停止ボタンを押すと**CLIで走らせているジョブも止まる**（開いているだけなら影響なし）。止まった場合はCLIが exit 1 で明示的に失敗するので、黙って欠落することはない
- `--timeout`（既定900秒）は**キュー待ち時間も含む**。大量枚数（目安 `-n 15` 以上）や重い解像度では伸ばすこと。タイムアウトしても画像が壊れるわけではなく、サーバ側の生成は走り続ける（out/には来ない）
- **steps を変えると同じseedでも構図が変わる**。過去に記録したseedレシピは、当時のstepsも一緒に指定しないと再現しない
- ネガティブに nsfw 系を入れてあるが**完全ではない**（肩出し・露出寄りは残る）。素材として使う前に必ず目視すること
- 生成が失敗した場合も途中まで落ちた画像は `out/` に残る。**呼び出し側は out/ をglobせず exit code を見ること**（成功時のみ exit 0）
- SDXLでの `1024x1024` は 24GB なら余裕。Flux系を入れるならGGUF量子化版を使うこと（fp16は入らない）
- モデルのライセンスは各配布元に従う。商用利用の可否はモデルごとに違う
