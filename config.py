import os
from pathlib import Path

from dotenv import load_dotenv

#Load .env file 
load_dotenv()

#Project paths
PROJECT_ROOT = Path(__file__).parent
MODEL_DIR = PROJECT_ROOT / "models"
DATA_DIR = PROJECT_ROOT / "data"
MODEL_PATH = MODEL_DIR / "disaster_classifier.pkl"
TRAINING_DATA_PATH = DATA_DIR / "train.csv"

#API keys 
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

#LLM settings
GROQ_MODEL_NAME = "llama-3.1-8b-instant"
LLM_TEMPERATURE = 0.2
LLM_MAX_TOKENS = 512

#Risk scoring weights 
RISK_WEIGHTS = {
    "ml_confidence": 30,       # Max points from ML confidence
    "urgency": 25,             # Max points from urgency level
    "source_absent": 10,       # Penalty if no credible source cited
    "evidence_absent": 10,     # Penalty if no evidence present
    "keyword_density": 15,     # Max points from crisis keyword density
    "message_length": 10,      # Max points from message length heuristic
}

#Risk level thresholds 
RISK_THRESHOLDS = {
    "low": 25,
    "medium": 50,
    "high": 75,
    # Anything above 75 is "Critical"
}

#Crisis keywords (used by risk scorer & fallback extractor) 
CRISIS_KEYWORDS = [
    "earthquake", "flood", "tsunami", "hurricane", "tornado",
    "wildfire", "fire", "explosion", "bombing", "attack",
    "shooting", "collapse", "derailment", "crash", "pandemic",
    "outbreak", "evacuation", "casualties", "dead", "killed",
    "injured", "trapped", "rescue", "emergency", "disaster",
    "destruction", "damage", "devastation", "storm", "cyclone",
    "landslide", "volcano", "eruption", "nuclear", "chemical",
    "bioterrorism", "hostage", "gunman", "active shooter",
]

#UI constants 
APP_TITLE = "Crisis Rumor Verification Agent"
APP_SUBTITLE = "AI-powered disaster message analysis & verification"
APP_ICON = ""
