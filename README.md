# 2027 W4R Step Challenge — Dashboard Prototype v2

A polished Streamlit prototype for the 2027 Walk for Resilience Step Challenge.

## Version 3 branding update

The supplied Viridian Foundation logo is now embedded directly in the dashboard header.

## Included in this version

- Branded dashboard-style home screen
- Total steps, kilometres, participants and active teams
- Challenge target progress bar
- Top-three team podium
- Total team leaderboard
- Average steps per participant for fairer team comparison
- Individual leaderboard
- Daily step entry form
- Recent activity view
- CSV download for administrators
- Sample data for testing

## Run locally

1. Install Python.
2. Open a terminal in this folder.
3. Install dependencies:

   pip install -r requirements.txt

4. Start:

   streamlit run app.py

## Add sample data

If you want to see the dashboard populated immediately:

- Rename `steps_sample.csv` to `steps.csv`, or
- Copy the rows from `steps_sample.csv` into a new `steps.csv`.

## Important before live launch

The current version saves step entries to `steps.csv`, which is fine for layout
testing but not appropriate as permanent multi-user storage on Streamlit Community
Cloud.

The live version should use a shared database such as PostgreSQL/Supabase.

## Settings you can easily change

At the top of `app.py` you can change:

- `TEAMS`
- `CHALLENGE_TARGET_STEPS`
- `KM_PER_STEP`
- Branding colours

## Branding

The current colours are placeholders inspired by the existing W4R/Viridian visual
direction. Replace them with the exact approved colour values when available.

We can also add image/logo files to the project and display them in the header/footer.
