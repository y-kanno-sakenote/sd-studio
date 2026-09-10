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
- 初回生成はモデルロードで数分かかる。2回目以降はキャッシュが効く
- SDXLでの `1024x1024` は 24GB なら余裕。Flux系を入れるならGGUF量子化版を使うこと（fp16は入らない）
- モデルのライセンスは各配布元に従う。商用利用の可否はモデルごとに違う
