import trimesh
import numpy as np

def glb_to_pointcloud_and_obj(glb_path, export_obj_path, npy_path):
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
glb_to_pointcloud_and_obj("./output/gemini/gemini_robot.glb", "./output/gemini/check_me.obj", "./output/gemini/output.npy")

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