import trimesh
import numpy as np
#面からランダムに点群を選ぶのでなく，メッシュの頂点を混ぜる
def glb_to_pointcloud_and_obj_mesh_points(glb_path, export_obj_path, npy_path):
    # 1. GLB読み込み
    mesh = trimesh.load(glb_path)
    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.dump(concatenate=True)

    # --- [SPECIAL FIX 1] 回転補正 (仰向け対策) ---
    print("--- Rotation Fixing ---")
    # ロボットの座標系に合わせて調整（前回うまくいった角度を採用してください）
    # 仰向けなら np.pi/2, うつ伏せなら -np.pi/2, 横向きならY軸回転などを試す
    matrix = trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0]) 
    mesh.apply_transform(matrix)
    mesh.apply_translation(-mesh.centroid)
    
    # 確認用OBJ保存
    mesh.export(export_obj_path)
    print(f"Saved OBJ: {export_obj_path}")

    # --- [SPECIAL FIX 2] 「ハイブリッド・サンプリング」 ---
    # 面積ベースだけでなく、形状の角（頂点）も混ぜて、細い足が消えるのを防ぐ
    
    target_count = 8192
    
    # A. 表面からランダムサンプリング (全体の7割くらい)
    count_surface = int(target_count * 0.7)
    points_surface, _ = trimesh.sample.sample_surface(mesh, count_surface)
    
    # B. メッシュの頂点をそのまま使う (全体の3割くらい)
    # 頂点は「足先」「関節」など重要な場所にあることが多い
    verts = mesh.vertices
    if len(verts) > 0:
        # 頂点数が足りなければ繰り返し使う、多ければランダムに間引く
        indices = np.random.choice(len(verts), target_count - count_surface, replace=(len(verts) < (target_count - count_surface)))
        points_verts = verts[indices]
    else:
        points_verts = np.empty((0, 3))

    # AとBを合体！
    points = np.vstack((points_surface, points_verts))
    
    # 色情報の取得（頂点カラーベースで簡易取得）
    # ※厳密にやるなら頂点インデックス追跡が必要ですが、今回は簡易的に最近傍法で色を取るか、
    #  もしくは一律グレーにして「形」だけで勝負させます（色誤認を防ぐため推奨）
    
    # 今回は「形」を認識させたいので、あえて色は「白」で統一してみます
    # （変なテクスチャ色が邪魔している可能性もあるため）
    colors = np.ones((len(points), 3), dtype=np.float32) # 全て白 (1.0, 1.0, 1.0)

    # データ結合 & 保存
    point_cloud_data = np.hstack((points, colors)).astype(np.float32)
    np.save(npy_path, point_cloud_data)
    print(f"Saved NPY with Hybrid Sampling: {npy_path}")

def glb_to_pointcloud_and_obj_random_points(glb_path, export_obj_path, npy_path):
    # 1. GLBを読み込む (trimeshはGLB対応)
    mesh = trimesh.load(glb_path)
    
    # Scene形式で読み込まれた場合は結合する（TripoのGLBはSceneになりがち）
    if isinstance(mesh, trimesh.Scene):
        # scene.dump(concatenate=True) を使うと一発で結合してくれます
        mesh = mesh.dump(concatenate=True)
    # =========================================================================
    # ★今回だけ特別：ロボットが「手」に見える問題の修正パッチ
    # =========================================================================
    print("--- [SPECIAL FIX] Applying Rotation (Z-up to Y-up) ---")
    
    # X軸を中心に -90度 回転させる行列を作成
    # これで「寝ている(Z-up)」ロボットを「立たせる(Y-up)」ことができます
    matrix = trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0])
    
    # メッシュ全体に回転を適用
    mesh.apply_transform(matrix)
    
    # ついでに位置も原点に合わせておきます（視界外へ飛ぶのを防ぐため）
    mesh.apply_translation(-mesh.centroid)
    print("--- [SPECIAL FIX] Rotation & Centering Done ---")
    # 2. ここでChoreonoid確認用のOBJを書き出してしまう
    mesh.export(export_obj_path)
    print(f"Choreonoid用OBJを保存しました: {export_obj_path}")

    # --- 以下、さっきと同じ点群処理 ---
    points, face_indices = trimesh.sample.sample_surface(mesh, 8192)
    
    # 色情報の取得 (GLBはvisual.vertex_colorsなどに入ることが多い)
    # 簡易的に色を取得
    if hasattr(mesh.visual, 'to_color'):
        mesh.visual = mesh.visual.to_color()

    colors = np.zeros((8192, 3))
    if hasattr(mesh.visual, 'face_colors'):
         colors = mesh.visual.face_colors[face_indices][:, :3]
    
    # 正規化 (0-1)
    # 正規化 (0-1)
    if colors.max() > 1.0:
        # astype(np.float32) で先に「小数の箱」に変換してから割る
        colors = colors.astype(np.float32) / 255.0

    # 座標などの処理...
    # (省略: さっきのコードの続き)
    
    point_cloud_data = np.hstack((points, colors)).astype(np.float32)
    np.save(npy_path, point_cloud_data)

# 実行
glb_to_pointcloud_and_obj_mesh_points("./output/gemini/gemini_robot.glb", "./output/gemini/check_me.obj", "./output/gemini/gemini_robot_normal_mesh_points.npy")

'''
import numpy as np
import trimesh

# ファイルパス（適宜書き換えてください）
input_obj_path = "./output/gemini/check_me.obj"
output_obj_path ="./output/gemini/fixed_gemini.obj"
output_npy_path = "./output/gemini/fixed_gemini.npy"

# 1. 読み込み
mesh = trimesh.load(input_obj_path)

# Scene形式なら結合（念のため）
if isinstance(mesh, trimesh.Scene):
    mesh = mesh.dump(concatenate=True)

# 2. 強制的にセンタリング（原点をモデルの中心に合わせる）
# これで「カメラの視界外に飛んでいく」のを防ぎます
mesh.apply_translation(-mesh.centroid)

# 3. スケールを100倍にする
# これで「小さすぎて見えない」を防ぎます
mesh.apply_scale(100.0)

# 4. 法線（Normals）の計算
# Trimeshは関数を呼ばなくても、アクセスするだけで勝手に計算してくれます
# 念のため一度アクセスして計算させておきます
_ = mesh.vertex_normals

# 5. 色を「明るいグレー」にする（テクスチャトラブル回避）
# マテリアルをリセット
if hasattr(mesh.visual, 'material'):
    # シンプルな色設定で上書き
    try:
        mesh.visual.material = trimesh.visual.material.SimpleMaterial(
            diffuse=[200, 200, 200, 255],
            ambient=[200, 200, 200, 255]
        )
    except:
        pass # エラーが出たら無視

# 頂点カラーも上書き
if hasattr(mesh.visual, 'vertex_colors'):
    mesh.visual.vertex_colors = np.ones((len(mesh.vertices), 4)) * [200, 200, 200, 255]

# 6. 保存（include_normals=True で法線付きで保存）
mesh.export(output_obj_path, include_normals=True)

print(f"修正完了: {output_obj_path}")
print(f"- 位置: 原点(0,0,0)に移動済み")
print(f"- サイズ: 100倍")
'''