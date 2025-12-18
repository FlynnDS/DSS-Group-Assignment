import pandas as pd

def calculate_binned_error(rating, actual_value):
    """
    Calculate error using binned approach where each rating represents a range:
    Rating 1: [0.00, 0.20) - Very Low
    Rating 2: [0.20, 0.40) - Low
    Rating 3: [0.40, 0.60) - Moderate
    Rating 4: [0.60, 0.80) - High
    Rating 5: [0.80, 1.00] - Very High
    
    If actual value is within the bin, error = 0
    If outside, error = distance to nearest boundary
    """
    # Define bin boundaries
    bins = [(0.00, 0.20), (0.20, 0.40), (0.40, 0.60), (0.60, 0.80), (0.80, 1.00)]
    
    # Get the bin for this rating (rating is 1-5, bins are indexed 0-4)
    lower, upper = bins[int(rating) - 1]
    
    # Check if actual value is within the bin
    if lower <= actual_value <= upper:
        return 0.0
    elif actual_value < lower:
        return lower - actual_value
    else:  # actual_value > upper
        return actual_value - upper

# Load data
df = pd.read_csv('responses_backup_20251130_2.csv')
songs_df = pd.read_csv('../data/candDSS.csv')
survey1_df = pd.read_csv('../data/dss_data22nov.csv')

# Get musical sophistication variables
ms_data = survey1_df[['email', 'MSAE', 'MSE']].copy()
ms_data['email'] = ms_data['email'].str.lower().str.strip()
df['email_clean'] = df['email'].str.lower().str.strip()

# Merge musical sophistication
df = df.merge(ms_data, left_on='email_clean', right_on='email', how='left', suffixes=('', '_ms'))
print(f"✓ Merged musical sophistication: {df['MSAE'].notna().sum()}/{len(df)} participants")

# ============================================================================
# 1. Prepare Rating Data (for RQ, SQ1, SQ2)
# ============================================================================
rating_data = []

for _, row in df.iterrows():
    participant_id = row['email']
    important = row['important_characteristics'].lower()
    has_all_four = all(f in important for f in ['danceability', 'valence', 'energy', 'acousticness'])
    
    msae = row['MSAE'] if pd.notna(row['MSAE']) else None
    mse = row['MSE'] if pd.notna(row['MSE']) else None
    
    for i in range(8):
        bucket = row[f'song_{i}_bucket']
        rating = row[f'song_{i}_rating']
        
        if pd.notna(bucket) and pd.notna(rating):
            same_genre = 1 if 'same_genre' in bucket else 0
            same_features = 1 if 'dissimilar' not in bucket else 0
            
            rating_data.append({
                'participant_id': participant_id,
                'rating': rating,
                'same_genre': same_genre,
                'same_features': same_features,
                'selected_all_features': 1 if has_all_four else 0,
                'selected_danceability': 1 if 'danceability' in important else 0,
                'selected_valence': 1 if 'valence' in important else 0,
                'selected_energy': 1 if 'energy' in important else 0,
                'selected_acousticness': 1 if 'acousticness' in important else 0,
                'MSAE': msae,
                'MSE': mse
            })

rating_df = pd.DataFrame(rating_data)
rating_df.to_csv('rating_data_long.csv', index=False)
print(f'✓ rating_data_long.csv: {len(rating_df)} ratings from {rating_df.participant_id.nunique()} participants')

# ============================================================================
# 2. Prepare Perception Data (for SQ3)
# ============================================================================
perception_data = []

for _, row in df.iterrows():
    participant_id = row['email']
    important = row['important_characteristics'].lower()
    
    msae = row['MSAE'] if pd.notna(row['MSAE']) else None
    mse = row['MSE'] if pd.notna(row['MSE']) else None
    
    for i in range(8):
        track_name = row[f'song_{i}_track']
        
        if pd.notna(track_name):
            song_data = songs_df[songs_df['trackname'] == track_name]
            
            if not song_data.empty:
                song_actual = song_data.iloc[0]
                
                for feature in ['danceability', 'valence', 'energy', 'acousticness']:
                    perceived = row[f'song_{i}_{feature}']
                    actual = song_actual[feature]
                    
                    if pd.notna(perceived) and pd.notna(actual):
                        error = calculate_binned_error(perceived, actual)
                        is_important = 1 if feature in important else 0
                        
                        perception_data.append({
                            'participant_id': participant_id,
                            'feature': feature,
                            'perceived_rating': perceived,
                            'actual': actual,
                            'error': error,
                            'feature_is_important': is_important,
                            'MSAE': msae,
                            'MSE': mse
                        })

perception_df = pd.DataFrame(perception_data)
perception_df.to_csv('perception_data_long.csv', index=False)
print(f'✓ perception_data_long.csv: {len(perception_df)} perceptions from {perception_df.participant_id.nunique()} participants')

