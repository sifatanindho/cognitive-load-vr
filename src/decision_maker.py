import os
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
    x, y, z = dimensions
    structure = np.empty((x, y, z), dtype=str)
    colors = ['R', 'B', 'G', 'Y']
    for i in range(x):
        for j in range(y):
            for k in range(z):
                if i == 0:  # bottom layer always got blocks
                    structure[i, j, k] = np.random.choice(colors)
                else:
                    if structure[i-1, j, k] != '': # we ain't letting blocks float
                        if np.random.rand() > 0.3:  # 70% chance to add a block on top
                            structure[i, j, k] = np.random.choice(colors)
                        else:
                            structure[i, j, k] = ''
                    else:
                        structure[i, j, k] = ''
    return structure

def plot_lego_structure_3d(structure):
    color_map = {
        'R': 'red',
        'B': 'blue',
        'G': 'green',
        'Y': 'yellow',
        '': 'white'
    }
    x, y, z, colors = [], [], [], []
    for i in range(structure.shape[0]):
        for j in range(structure.shape[1]):
            for k in range(structure.shape[2]):
                if structure[i, j, k] != '':
                    x.append(i)
                    y.append(j)
                    z.append(k)
                    colors.append(color_map.get(structure[i, j, k], 'white'))
    fig = go.Figure(data=[
        go.Scatter3d(
            x=x,
            y=y,
            z=z,
            mode='markers',
            marker=dict(
                size=10,
                color=colors,
                opacity=0.8,
                symbol='square'
            )
        )
    ])
    fig.update_layout(
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z',
            aspectratio=dict(x=1, y=1, z=1),
            bgcolor='white'
        ),
        title="3D Lego Structure",
        margin=dict(l=0, r=0, b=0, t=30)
    )
    
    fig.show()

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