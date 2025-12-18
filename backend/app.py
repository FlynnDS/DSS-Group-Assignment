#!/usr/bin/env python3
"""
Simple Flask backend to collect follow-up survey responses
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import csv
import os
from datetime import datetime

app = Flask(__name__, static_folder='.')
CORS(app)  # Enable CORS for local testing

# Data storage files
RESPONSES_DIR = "survey_responses"
JSON_FILE = os.path.join(RESPONSES_DIR, "all_responses.json")
CSV_FILE = os.path.join(RESPONSES_DIR, "responses.csv")

# Create responses directory if it doesn't exist
os.makedirs(RESPONSES_DIR, exist_ok=True)

def initialize_csv():
    """Initialize CSV file with headers if it doesn't exist"""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow([
                'timestamp', 'email', 'quotes_consent', 'important_characteristics',
                'song_0_track', 'song_0_artist', 'song_0_bucket', 'song_0_rating',
                'song_0_danceability', 'song_0_liveness', 'song_0_valence', 
                'song_0_energy', 'song_0_acousticness',
                'song_1_track', 'song_1_artist', 'song_1_bucket', 'song_1_rating',
                'song_1_danceability', 'song_1_liveness', 'song_1_valence', 
                'song_1_energy', 'song_1_acousticness',
                'song_2_track', 'song_2_artist', 'song_2_bucket', 'song_2_rating',
                'song_2_danceability', 'song_2_liveness', 'song_2_valence', 
                'song_2_energy', 'song_2_acousticness',
                'song_3_track', 'song_3_artist', 'song_3_bucket', 'song_3_rating',
                'song_3_danceability', 'song_3_liveness', 'song_3_valence', 
                'song_3_energy', 'song_3_acousticness',
                'song_4_track', 'song_4_artist', 'song_4_bucket', 'song_4_rating',
                'song_4_danceability', 'song_4_liveness', 'song_4_valence', 
                'song_4_energy', 'song_4_acousticness',
                'song_5_track', 'song_5_artist', 'song_5_bucket', 'song_5_rating',
                'song_5_danceability', 'song_5_liveness', 'song_5_valence', 
                'song_5_energy', 'song_5_acousticness',
                'song_6_track', 'song_6_artist', 'song_6_bucket', 'song_6_rating',
                'song_6_danceability', 'song_6_liveness', 'song_6_valence', 
                'song_6_energy', 'song_6_acousticness',
                'song_7_track', 'song_7_artist', 'song_7_bucket', 'song_7_rating',
                'song_7_danceability', 'song_7_liveness', 'song_7_valence', 
                'song_7_energy', 'song_7_acousticness'
            ])

def save_to_json(data):
    """Save response to JSON file"""
    # Load existing data
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
    else:
        all_data = []
    
    # Append new response
    all_data.append(data)
    
    # Save updated data
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)

def save_to_csv(data):
    """Save response to CSV file"""
    initialize_csv()
    
    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Prepare row data
        row = [
            data['timestamp'],
            data['email'],
            data['quotesConsent'],
            ';'.join(data['importantCharacteristics'])
        ]
        
        # Add data for each of 8 songs
        for i in range(8):
            song_key = str(i)
            if song_key in data['responses']:
                song = data['responses'][song_key]
                row.extend([
                    song['trackname'],
                    song['artist'],
                    song['bucket'],
                    song['rating'],
                    song['characteristics']['danceability'],
                    song['characteristics']['liveness'],
                    song['characteristics']['valence'],
                    song['characteristics']['energy'],
                    song['characteristics']['acousticness']
                ])
            else:
                # Fill with empty values if song not present
                row.extend([''] * 9)
        
        writer.writerow(row)

@app.route('/api/submit', methods=['POST'])
def submit_response():
    """Handle survey submission"""
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('email') or not data.get('responses'):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Save to both JSON and CSV
        save_to_json(data)
        save_to_csv(data)
        
        print(f"✓ Saved response from {data['email']}")
        
        return jsonify({
            'success': True,
            'message': 'Response saved successfully'
        }), 200
        
    except Exception as e:
        print(f"✗ Error saving response: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/')
def index():
    """Serve the consent page"""
    return send_from_directory('.', 'followup_consent.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('.', path)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'responses_collected': len(get_all_responses())
    })

def get_all_responses():
    """Get all collected responses"""
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics about collected responses"""
    responses = get_all_responses()
    
    return jsonify({
        'total_responses': len(responses),
        'participants': [r['email'] for r in responses]
    })

@app.route('/api/download/json', methods=['GET'])
def download_json():
    """Download all responses as JSON"""
    return send_from_directory(RESPONSES_DIR, 'all_responses.json', as_attachment=True)

@app.route('/api/download/csv', methods=['GET'])
def download_csv():
    """Download all responses as CSV"""
    return send_from_directory(RESPONSES_DIR, 'responses.csv', as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    
    print("=" * 60)
    print("Starting Follow-up Survey Backend Server")
    print("=" * 60)
    print(f"Data will be saved to: {os.path.abspath(RESPONSES_DIR)}")
    print("Endpoints:")
    print("  - POST /api/submit       - Submit survey response")
    print("  - GET  /api/health       - Health check")
    print("  - GET  /api/stats        - View statistics")
    print("=" * 60)
    print(f"\nServer running on port {port}")
    print("Press Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=port, debug=False)

