import os

# 出力フォルダを指定（変更していなければ output/ のままでOK）
OUTPUT_DIR = "output/0"
OBJ_NAME = "mesh.obj"

# テクスチャ画像のファイル名を探す
texture_file = None
files = os.listdir(OUTPUT_DIR)
for f in files:
    if f.endswith(".png"):
        texture_file = f
        break

if not texture_file:
    print(f"エラー: {OUTPUT_DIR} フォルダ内に .png ファイルが見つかりません。")
    exit()

obj_path = os.path.join(OUTPUT_DIR, OBJ_NAME)
mtl_name = "mesh.mtl"
mtl_path = os.path.join(OUTPUT_DIR, mtl_name)

# 1. mesh.mtl ファイルを作成
mtl_content = f"""newmtl material_0
Ka 1.000 1.000 1.000
Kd 1.000 1.000 1.000
Ks 0.000 0.000 0.000
map_Kd {texture_file}
"""

with open(mtl_path, "w") as f:
    f.write(mtl_content)
print(f"作成しました: {mtl_path}")

# 2. mesh.obj を書き換えて mtl を紐付ける
with open(obj_path, "r") as f:
    lines = f.readlines()

new_lines = []
has_mtllib = False
has_usemtl = False
faces_started = False

# 既に記載があるかチェック
if any("mtllib" in l for l in lines):
    has_mtllib = True
    print("情報: OBJファイルには既に mtllib の記述があります。")

if any("usemtl" in l for l in lines):
    has_usemtl = True
    print("情報: OBJファイルには既に usemtl の記述があります。")

# 修正処理
if not has_mtllib:
    new_lines.append(f"mtllib {mtl_name}\n")
else:
    # 既存の行をそのまま使うのでここでは何もしない（ループ内で処理）
    pass

for line in lines:
    # mtllibがなくて、まだ書き込んでない場合、ファイルの先頭に追加済み
    
    # 最初の面データ(f ...)が来る直前に usemtl を挿入
    if line.startswith("f ") and not faces_started:
        faces_started = True
        if not has_usemtl:
            new_lines.append("usemtl material_0\n")
    
    new_lines.append(line)

# 上書き保存
with open(obj_path, "w") as f:
    f.writelines(new_lines)

print(f"修正しました: {obj_path}")
print("完了！Choreonoidで mesh.obj を読み込み直してください。")