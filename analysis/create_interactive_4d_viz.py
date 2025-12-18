import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

print("Loading data...")

# Load all datasets
recs_df = pd.read_excel('../data/all_recs_with_email.xlsx')
songs_df = pd.read_csv('../data/candDSS.csv')
survey_df = pd.read_csv('responses_backup_20251130_2.csv')
user_data_df = pd.read_csv('../data/dss_data22nov.csv')

# Pick the example user
example_email = 'harryhall3698@gmail.com'
example_user = survey_df[survey_df['email'] == example_email].iloc[0]

print(f"Creating interactive 4D visualization for user: {example_email}")

# Get user's profile from original study
user_subject = user_data_df[user_data_df['email'] == example_email]['subject'].iloc[0]
user_profile_data = user_data_df[user_data_df['subject'] == user_subject]

# Calculate user's ACTUAL feature profile from their liked songs
song_ratings = {}
for col in user_profile_data.columns:
    if col.startswith('s') and col.endswith('r') and col[1:-1].isdigit():
        song_id = int(col[1:-1])
        rating = user_profile_data[f's{song_id}r'].values[0]
        if pd.notna(rating) and rating >= 4:
            song_ratings[song_id] = rating

# Get the actual features of those songs
liked_features = []
for song_id in song_ratings.keys():
    song_data = songs_df[songs_df['id'] == song_id]
    if len(song_data) > 0:
        liked_features.append({
            'danceability': song_data['danceability'].values[0],
            'valence': song_data['valence'].values[0],
            'energy': song_data['energy'].values[0],
            'acousticness': song_data['acousticness'].values[0]
        })

# Calculate user profile
if len(liked_features) > 0:
    user_profile = {
        'danceability': np.mean([f['danceability'] for f in liked_features]),
        'valence': np.mean([f['valence'] for f in liked_features]),
        'energy': np.mean([f['energy'] for f in liked_features]),
        'acousticness': np.mean([f['acousticness'] for f in liked_features])
    }
else:
    user_profile = {'danceability': 0.5, 'valence': 0.5, 'energy': 0.5, 'acousticness': 0.5}

print(f"User profile: D={user_profile['danceability']:.3f}, V={user_profile['valence']:.3f}, E={user_profile['energy']:.3f}, A={user_profile['acousticness']:.3f}")

# Get recommendations
user_recs = recs_df[recs_df['email'] == example_email]
user_recs_with_features = user_recs.merge(songs_df[['trackname', 'danceability', 'valence', 'energy', 'acousticness']], 
                                         on='trackname', how='left')

# Calculate distances
def euclidean_distance(song_features, user_profile):
    return np.sqrt(sum((song_features[feat] - user_profile[feat])**2 
                      for feat in ['danceability', 'valence', 'energy', 'acousticness']))

user_recs_with_features['distance'] = user_recs_with_features.apply(
    lambda row: euclidean_distance(row, user_profile), axis=1
)

# Get user ratings
for idx, row in user_recs_with_features.iterrows():
    track = row['trackname']
    for i in range(8):
        if example_user[f'song_{i}_track'] == track:
            user_recs_with_features.loc[idx, 'user_rating'] = example_user[f'song_{i}_rating']
            break

# Color mapping
bucket_colors = {
    'diff_genre_similar': '#2E7D32',      # Dark green
    'same_genre_similar': '#81C784',      # Light green
    'same_genre_dissimilar': '#FF6B6B',   # Coral/red  
    'diff_genre_dissimilar': '#9C27B0'    # Purple
}

bucket_labels = {
    'diff_genre_similar': 'Different Genre, Similar Features',
    'same_genre_similar': 'Same Genre, Similar Features',
    'same_genre_dissimilar': 'Same Genre, Different Features', 
    'diff_genre_dissimilar': 'Different Genre, Different Features'
}

# ============================================================================
# Create Interactive 3D Subplots
# ============================================================================

# Create 2x2 subplots
fig = make_subplots(
    rows=2, cols=2,
    specs=[[{'type': 'scatter3d'}, {'type': 'scatter3d'}],
           [{'type': 'scatter3d'}, {'type': 'scatter3d'}]],
    subplot_titles=('Danceability vs Valence vs Energy',
                   'Danceability vs Valence vs Acousticness',
                   'Danceability vs Energy vs Acousticness',
                   'Valence vs Energy vs Acousticness'),
    vertical_spacing=0.02,
    horizontal_spacing=0.01
)

views = [
    {'axes': ['danceability', 'valence', 'energy'], 'row': 1, 'col': 1},
    {'axes': ['danceability', 'valence', 'acousticness'], 'row': 1, 'col': 2},
    {'axes': ['danceability', 'energy', 'acousticness'], 'row': 2, 'col': 1},
    {'axes': ['valence', 'energy', 'acousticness'], 'row': 2, 'col': 2}
]

for view_idx, view in enumerate(views):
    # Add user profile star
    user_x = user_profile[view['axes'][0]]
    user_y = user_profile[view['axes'][1]]
    user_z = user_profile[view['axes'][2]]
    
    fig.add_trace(
        go.Scatter3d(
            x=[user_x],
            y=[user_y],
            z=[user_z],
            mode='markers',
            marker=dict(
                size=15,
                color='gold',
                symbol='diamond',
                line=dict(color='black', width=2)
            ),
            name='User Profile',
            text=['User Profile'],
            hovertemplate=f'<b>User Profile</b><br>' +
                         f'{view["axes"][0].capitalize()}: {user_x:.3f}<br>' +
                         f'{view["axes"][1].capitalize()}: {user_y:.3f}<br>' +
                         f'{view["axes"][2].capitalize()}: {user_z:.3f}<br>' +
                         '<extra></extra>',
            showlegend=(view_idx == 0)
        ),
        row=view['row'], col=view['col']
    )
    
    # Add songs by bucket
    for bucket, color in bucket_colors.items():
        bucket_data = user_recs_with_features[user_recs_with_features['bucket'] == bucket]
        
        if len(bucket_data) > 0:
            x = bucket_data[view['axes'][0]].values
            y = bucket_data[view['axes'][1]].values
            z = bucket_data[view['axes'][2]].values
            
            hover_text = []
            for idx, row in bucket_data.iterrows():
                text = (f"<b>{row['trackname']}</b><br>" +
                       f"Distance: {row['distance']:.3f}<br>" +
                       f"Rating: {row['user_rating']:.0f}/5<br>" +
                       f"Danceability: {row['danceability']:.3f}<br>" +
                       f"Valence: {row['valence']:.3f}<br>" +
                       f"Energy: {row['energy']:.3f}<br>" +
                       f"Acousticness: {row['acousticness']:.3f}")
                hover_text.append(text)
            
            fig.add_trace(
                go.Scatter3d(
                    x=x,
                    y=y,
                    z=z,
                    mode='markers',
                    marker=dict(
                        size=8,
                        color=color,
                        line=dict(color='black', width=1)
                    ),
                    name=bucket_labels[bucket],
                    text=hover_text,
                    hovertemplate='%{text}<extra></extra>',
                    showlegend=(view_idx == 0)
                ),
                row=view['row'], col=view['col']
            )
            
            # Add distance lines
            for idx, row in bucket_data.iterrows():
                song_x = row[view['axes'][0]]
                song_y = row[view['axes'][1]]
                song_z = row[view['axes'][2]]
                
                fig.add_trace(
                    go.Scatter3d(
                        x=[user_x, song_x],
                        y=[user_y, song_y],
                        z=[user_z, song_z],
                        mode='lines',
                        line=dict(color=color, width=2),
                        showlegend=False,
                        hoverinfo='skip'
                    ),
                    row=view['row'], col=view['col']
                )
    
    # Update axes
    scene_dict = dict(
        xaxis=dict(title=view['axes'][0].capitalize(), range=[0, 1]),
        yaxis=dict(title=view['axes'][1].capitalize(), range=[0, 1]),
        zaxis=dict(title=view['axes'][2].capitalize(), range=[0, 1]),
        camera=dict(
            eye=dict(x=1.5, y=1.5, z=1.3)
        )
    )
    
    if view['row'] == 1 and view['col'] == 1:
        fig.update_scenes(scene_dict, row=1, col=1)
    elif view['row'] == 1 and view['col'] == 2:
        fig.update_scenes(scene_dict, row=1, col=2)
    elif view['row'] == 2 and view['col'] == 1:
        fig.update_scenes(scene_dict, row=2, col=1)
    else:
        fig.update_scenes(scene_dict, row=2, col=2)

# Update layout
fig.update_layout(
    title=dict(
        text=f'Interactive 4D Feature Space Visualization<br>' +
             f'<sub>Participant: {example_email} | Rotate, zoom, and hover for details</sub>',
        x=0.5,
        xanchor='center'
    ),
    height=1000,
    showlegend=True,
    legend=dict(
        x=0.98,
        y=0.98,
        xanchor='right',
        yanchor='top',
        bgcolor='rgba(255,255,255,0.9)',
        bordercolor='black',
        borderwidth=1
    ),
    hovermode='closest'
)

# Save interactive HTML
output_file = '../figures/4D_interactive_visualization.html'
fig.write_html(output_file)
print(f"\nSaved interactive visualization: {output_file}")
print("   Open this file in your browser to explore the 4D space interactively!")






