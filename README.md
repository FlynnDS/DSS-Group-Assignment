# Project Structure

This repository is organized into separate folders for deployment and analysis.

**Live Survey:** https://dssfollowupsurvey-production.up.railway.app/

## Folder Overview

```
DSS-Group-Assignment/
│
├── backend/              # Railway deployment files ONLY
│   ├── app.py           # Flask backend
│   ├── requirements.txt
│   ├── Procfile
│   ├── followup_*.html  # Survey pages
│   └── *.csv (symlinks) # Links to data files
│
├── preprocessing/       # Recommendation generation (run ONCE)
│   ├── Group Project.ipynb         # Generate recommendations
│   └── prepare_recommendations.py  # Convert to JSON
│
├── data/                # Shared data files
│   ├── candDSS.csv      # Song features
│   ├── dss_data22nov.csv # User profiles & MSI scores
│   ├── recommendations_data.json # Recommendations in .json for backend
│   ├── all_recs_with_email.xlsx # Recommendations table
│   └── cleaned_musicdata.csv    # User profiles + ratings
│
├── analysis/            # Local analysis scripts (Survey 2 results)
│   ├── analyze_results.py          # Generate plots
│   ├── statistical_analysis.R      # Mixed-effects models
│   ├── prepare_data_for_r.py       # Data preprocessing
│   ├── create_interactive_4d_viz.py
│   ├── responses_backup_*.csv      # Survey responses
│   ├── rating_data_long.csv        # R input data
│   └── perception_data_long.csv    # R input data
│
├── figures/             # Generated plots
│   ├── RQ_genre_feature_interaction.png
│   ├── SQ1_feature_compensation.png
│   ├── SQ2_feature_awareness.png
│   ├── SQ3_perception_accuracy.png
│   ├── SQ4_musical_sophistication.png
│   └── 4D_interactive_visualization.html
│
├── docs/                # Documentation & assets
│   ├── Algorithm.png
│   ├── Consent_DSS.pdf
│   ├── email_template.txt
│   └── userProfile*.png
│
└── README.md            # Main project documentation
```

## Preprocessing - Generating Recommendations

**Run ONCE to generate recommendations from Survey 1 data:**

```bash
# Step 1: Open Jupyter Notebook
cd preprocessing
jupyter notebook "Group Project.ipynb"
# Run all cells to generate all_recs_with_email.xlsx

# Step 2: Convert to JSON for backend
python prepare_recommendations.py
```

**Outputs go to `data/` folder and are used by both backend and analysis.**

Only rerun if Survey 1 data changes or algorithm is modified.

## Deploying to Railway

**Only the `backend/` folder needs to be deployed:**

```bash
cd backend
railway up
```

Railway will:
- Install dependencies from `requirements.txt`
- Start the Flask app using `Procfile`
- Serve the survey at your Railway URL

**Live Survey URL:** https://dssfollowupsurvey-production.up.railway.app/

## Running Analysis Locally

```bash
# Generate all plots
cd analysis
python analyze_results.py

# Prepare data for R
python prepare_data_for_r.py

# Run statistical analysis
Rscript statistical_analysis.R > statistical_results_clean.txt

# Create 4D visualization
python create_interactive_4d_viz.py
```

## File Dependencies

### Preprocessing (run first):
- **Input:** `data/dss_data22nov.csv`, `data/candDSS.csv`
- **Output:** `data/all_recs_with_email.xlsx`, `data/recommendations_data.json`, `data/cleaned_musicdata.csv`
- **Run once** to generate recommendations

### Backend depends on:
- `data/` folder (via symlinks)
  - Especially: `recommendations_data.json`
- Survey HTML files

### Analysis depends on:
- `data/` folder
- `responses_backup_*.csv` (downloaded from Railway)
- Output goes to `figures/` folder

## Complete Workflow

### Initial Setup (Done Once):
0. **Generate Recommendations** → Run `preprocessing/Group Project.ipynb` and `prepare_recommendations.py`

### Survey Collection:
1. **Deploy Backend** → Railway backend serves Survey 2
2. **Collect Responses** → Railway backend collects responses

### Data Analysis:
3. **Download Responses** → Save to `analysis/responses_backup_*.csv`
4. **Run Python Analysis** → `cd analysis && python analyze_results.py`
5. **Run R Analysis** → `cd analysis && Rscript statistical_analysis.R`
6. **Use Figures** → Reference from `figures/` in LaTeX paper

## Mapping Scripts to Paper Results

All results in the paper Section \ref{sec:results} are generated from the following scripts:

### Python Script: `analysis/analyze_results.py`
Generates all figures (descriptive visualizations):

- **Figure \ref{fig:sq1_interaction}** → `figures/RQ_genre_feature_interaction.png`
  - Shows 2×2 interaction: genre × feature similarity
  
- **Figure \ref{fig:sq1_compensation}** → `figures/SQ1_feature_compensation.png`
  - Direct comparison for H1 testing
  
- **Figure \ref{fig:sq2_awareness}** → `figures/SQ2_feature_awareness.png`
  - All 4 features selected vs. not (H2)
  
- **Figure \ref{fig:sq2_individual}** → `figures/SQ2_individual_features.png`
  - Individual feature selection effects (H2)
  
- **Figure \ref{fig:sq3_perception}** → `figures/SQ3_perception_accuracy.png`
  - Perception accuracy by feature importance (H3)
  
- **Figure \ref{fig:sq4_sophistication}** → `figures/SQ4_musical_sophistication.png`
  - Musical sophistication correlations (H4)

### R Script: `analysis/statistical_analysis.R`
Generates all statistical tests (mixed-effects models):

- **Table \ref{tab:sq1_results}** → RQ: Genre × Feature Interaction (H1)
- **Table \ref{tab:sq2_results}** → SQ2: Individual feature effects (H2)
- **Table \ref{tab:sq3_results}** → SQ3: Feature importance on perception (H3)
- **Table \ref{tab:sq4_results}** → SQ4: Musical sophistication effects (H4)

Output saved to: `analysis/statistical_results_clean.txt`

### Data Files:
- **Long-format rating data** → `analysis/rating_data_long.csv` (prepared by `prepare_data_for_r.py`)
- **Long-format perception data** → `analysis/perception_data_long.csv` (prepared by `prepare_data_for_r.py`)

**Note:** All scripts contain inline comments mapping outputs to specific paper sections, tables, and figures.

