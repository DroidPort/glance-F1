import os

# Global Variables
NEXT_RACE_API_URL = "http://localhost:4463/f1/next_race/"

# For caching, the default polling time is 1 hour
default_expire = 3600


nationality_map = {
    "British": "Great Britain",
    "Dutch": "Netherlands",
    "Monegasque": "Monaco",
    "Thai": "Thailand",
    "Argentine": "Argentina",
    "New Zealander": "New Zealand",
    "Australian": "Australia",
    "French": "France",
    "Spanish": "Spain",
    "German": "Germany",
    "Canadian": "Canada",
    "Italian": "Italy",
    "Japanese": "Japan",
    "Brazilian": "Brazil",
    "Mexican": "Mexico",
    "Chinese": "China",
    "Finnish": "Finland",
    "American": "United States",
    "Austrian": "Austria"
    }