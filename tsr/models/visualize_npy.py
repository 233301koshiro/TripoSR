import numpy as np
import matplotlib.pyplot as plt

# ファイルパスを指定
file_path = "./output/gemini/gemini_robot_normal_mesh_points.npy"  # ←ここを自分のファイルに変える

try:
    data = np.load(file_path)
    print(f"Shape: {data.shape}")
    
    # (N, 3) 座標のみ か (N, 6) 色付き か確認
    points = data[:, :3]
    
    # 3Dプロット
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # 点が多すぎると重いので間引いて表示
    step = max(1, len(points) // 2048)
    ax.scatter(points[::step, 0], points[::step, 1], points[::step, 2], s=1)
    
    # 軸ラベル（これで向きを確認）
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    
    # 軸のスケールを揃える（歪み防止）
    max_range = np.array([points[:, 0].max()-points[:, 0].min(), 
                          points[:, 1].max()-points[:, 1].min(), 
                          points[:, 2].max()-points[:, 2].min()]).max() / 2.0
    mid_x = (points[:, 0].max()+points[:, 0].min()) * 0.5
    mid_y = (points[:, 1].max()+points[:, 1].min()) * 0.5
    mid_z = (points[:, 2].max()+points[:, 2].min()) * 0.5
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)

    plt.show()

except Exception as e:
    print(f"Error: {e}")