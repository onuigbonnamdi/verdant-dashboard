# Verdant Innovations — Smart Grid Dashboard

AI-powered UK energy demand forecasting dashboard built with Streamlit.

## Features
- Live UK grid demand data (Elexon BMRS API via Supabase)
- 48-hour AI demand forecast with confidence intervals
- Real-time weather data (temperature, wind, solar)
- System status monitoring
- Auto-refresh every 5 minutes

## Deploy on Streamlit Cloud

1. Push this repo to GitHub
2. Go to share.streamlit.io
3. Connect repo → set main file as `app.py`
4. Add secrets in Streamlit Cloud settings:
   - SUPABASE_URL
   - SUPABASE_KEY

## Secrets format (in Streamlit Cloud)
```
SUPABASE_URL = "https://bvxdfmfjcfjhubtbqqor.supabase.co"
SUPABASE_KEY = "your-anon-key-here"
```
