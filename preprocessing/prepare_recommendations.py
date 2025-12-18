import pandas as pd
import json

# Read the recommendations with email
recs_df = pd.read_excel("all_recs_with_email.xlsx")

# Read the song database to get Spotify URLs and other info
songs_df = pd.read_csv("candDSS.csv")

# Merge recommendations with song details
recs_with_details = recs_df.merge(
    songs_df[['trackname', 'spotifyurl', 'firstartist', 'imageurl', 'track_id']], 
    on='trackname', 
    how='left'
)

# Group by email
recommendations_by_email = {}

for email in recs_with_details['email'].unique():
    if pd.isna(email):
        continue
    
    user_recs = recs_with_details[recs_with_details['email'] == email].copy()
    
    # Convert to list of dictionaries
    recs_list = []
    for _, row in user_recs.iterrows():
        recs_list.append({
            'trackname': row['trackname'],
            'artist': row['firstartist'] if 'firstartist' in row else '',
            'spotifyurl': row['spotifyurl'] if 'spotifyurl' in row else '',
            'imageurl': row['imageurl'] if 'imageurl' in row else '',
            'track_id': row['track_id'] if 'track_id' in row else '',
            'bucket': row['bucket'] if 'bucket' in row else ''
        })
    
    recommendations_by_email[email.lower()] = recs_list

# Save to JSON
with open('recommendations_data.json', 'w') as f:
    json.dump(recommendations_by_email, f, indent=2)

print(f"Successfully processed recommendations for {len(recommendations_by_email)} participants")
print(f"Total recommendations: {len(recs_with_details)}")

