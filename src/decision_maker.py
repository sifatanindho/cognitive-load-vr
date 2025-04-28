import os
import random
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

def recommend_task(cognitive_load):
    load_to_difficulty = {
        "Very Low": 5, 
        "Low": 4,
        "Medium": 3,
        "High": 2,
        "Very High": 1
    }
    return load_to_difficulty.get(cognitive_load, 3) # defaulting to medium if input is not found

def get_number_of_blocks(recommended_task):
    difficulty_to_blocks = {
        5: (6, 6, 6),
        4: (5, 5, 5),
        3: (4, 4, 4),
        2: (3, 3, 3),
        1: (2, 2, 2)
    }
    return difficulty_to_blocks.get(recommended_task, (4, 4, 4))

def generate_lego_structure(dimensions):
    x_dim, y_dim, z_dim = dimensions
    structure = np.full((x_dim, y_dim, z_dim), '', dtype='<U1')
    for i in range(x_dim):
        for j in range(y_dim):
            structure[i, j, 0] = random.choice(['R', 'G', 'B', 'Y'])
    max_blocks = x_dim * y_dim * z_dim
    target_blocks = random.randint(int(0.4 * max_blocks), int(0.7 * max_blocks)) 
    blocks_placed = np.count_nonzero(structure)
    attempts = 0
    while blocks_placed < target_blocks and attempts < target_blocks * 10:
        x = random.randint(0, x_dim - 1)
        y = random.randint(0, y_dim - 1)
        z = random.randint(1, z_dim - 1)  
        if structure[x, y, z] == '' and structure[x, y, z-1] != '':
            structure[x, y, z] = random.choice(['R', 'G', 'B', 'Y'])
            blocks_placed += 1
        attempts += 1
    return structure


def plot_lego_structure_3d(structure):
    color_map = {
        'R': 'red',
        'B': 'blue',
        'G': 'green',
        'Y': 'yellow',
        '': 'white'
    }
    fig = go.Figure()
    cube_size = 0.9  
    for i in range(structure.shape[0]):
        for j in range(structure.shape[1]):
            for k in range(structure.shape[2]):
                if structure[i, j, k] != '':
                    color = color_map.get(structure[i, j, k], 'white')
                    fig.add_trace(make_cube(i, j, k, size=cube_size, color=color))
    fig.update_layout(
        scene=dict(
            xaxis=dict(nticks=structure.shape[0]+2, range=[-1, structure.shape[0]+1]),
            yaxis=dict(nticks=structure.shape[1]+2, range=[-1, structure.shape[1]+1]),
            zaxis=dict(nticks=structure.shape[2]+2, range=[-1, structure.shape[2]+1]),
            aspectratio=dict(x=1, y=1, z=1),
            bgcolor='white'
        ),
        title="3D Lego Structure (Cubes)",
        margin=dict(l=0, r=0, b=0, t=30),
        showlegend=False
    )
    fig.show()

def make_cube(x_center, y_center, z_center, size=1, color='blue'):
    d = size / 2
    x = [x_center-d, x_center+d, x_center+d, x_center-d, x_center-d, x_center+d, x_center+d, x_center-d]
    y = [y_center-d, y_center-d, y_center+d, y_center+d, y_center-d, y_center-d, y_center+d, y_center+d]
    z = [z_center-d, z_center-d, z_center-d, z_center-d, z_center+d, z_center+d, z_center+d, z_center+d]
    vertices = list(zip(x, y, z))
    I = [0, 0, 0, 1, 1, 2, 3, 4, 4, 5, 6, 7]
    J = [1, 3, 4, 2, 5, 3, 2, 5, 7, 6, 7, 6]
    K = [3, 4, 5, 3, 2, 7, 6, 7, 6, 2, 4, 5]
    return go.Mesh3d(
        x=x, y=y, z=z,
        i=I, j=J, k=K,
        color=color,
        opacity=1.0
    )

def plot_lego_sides(structure, save_path=None):
    sides = ['Front', 'Back', 'Left', 'Right']
    fig, axs = plt.subplots(1, 4, figsize=(16, 4))
    color_map = {
        'R': (1, 0, 0),    
        'B': (0, 0, 1),    
        'G': (0, 1, 0),    
        'Y': (1, 1, 0),    
        '': (1, 1, 1)      # rgb values bc imshow loves numbers
    }
    front = np.flipud(np.transpose(structure[:, -1, :]))   # x-z plane
    back = np.flipud(np.transpose(np.flip(structure[:, 0, :], axis=0)))  # x-z plane
    left = np.flipud(np.transpose(structure[0, :, :]))      # y-z plane
    right = np.flipud(np.transpose(np.flip(structure[-1, :, :], axis=0))) # y-z plane
    views = [front, back, left, right]
    if save_path:
        os.makedirs(save_path, exist_ok=True)

    for view, side in zip(views, sides):
        rgb_view = np.zeros((view.shape[0], view.shape[1], 3))
        for i in range(view.shape[0]):
            for j in range(view.shape[1]):
                rgb_view[i, j] = color_map.get(view[i, j], (1, 1, 1))

        rgb_view = np.fliplr(rgb_view)
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.imshow(rgb_view, interpolation='nearest')
        ax.set_title(side)
        ax.axis('off')
        plt.tight_layout()
        
        if save_path:
            filename = os.path.join(save_path, f"{side.lower()}.png")
            plt.savefig(filename)
            plt.close(fig)  
        else:
            plt.show()
    for ax, view, side in zip(axs, views, sides):
        rgb_view = np.zeros((view.shape[0], view.shape[1], 3))
        for i in range(view.shape[0]):
            for j in range(view.shape[1]):
                rgb_view[i, j] = color_map.get(view[i, j], (1, 1, 1))
        ax.imshow(rgb_view, interpolation='nearest')
        ax.set_title(side)
        ax.axis('off')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # just an example of how this module works
    predicted_load = "High"
    recommended_task = recommend_task(predicted_load)
    dimensions = get_number_of_blocks(recommended_task)
    print(f"Predicted Cognitive Load: {predicted_load}")
    print(f"Recommended Task Difficulty: {recommended_task}")
    lego_structure = generate_lego_structure(dimensions)
    plot_lego_sides(lego_structure, "./lego_images")
    plot_lego_structure_3d(lego_structure)