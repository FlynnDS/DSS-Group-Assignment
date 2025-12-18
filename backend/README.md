# Backend - Railway Deployment

This folder contains only the files needed for Railway deployment of the survey backend.

## Files Included:
- `app.py` - Flask backend application
- `requirements.txt` - Python dependencies
- `Procfile` - Railway start command
- `railway.json` - Railway configuration
- `followup_*.html` - Survey HTML pages
- Symlinks to data files in `../data/`

## Deploying to Railway:

1. Navigate to this folder:
```bash
cd backend
```

2. Deploy using Railway CLI:
```bash
railway up
```

Or push to Railway via Git from this directory.

## Local Testing:

```bash
python app.py
```

The server will run on http://localhost:5001

