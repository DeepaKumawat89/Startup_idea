from fastapi import FastAPI
from pydantic import BaseModel
import random
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# 🔐 Firebase init
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

app = FastAPI()

# ---------- DATA MODEL ----------
class Idea(BaseModel):
    name: str
    tagline: str
    description: str

# ---------- AI RATING LOGIC ----------
def calculate_rating(name, tagline, description):
    rating = random.randint(20, 60)
    desc = description.lower()

    if len(desc) > 80: rating += 10
    if len(desc) > 150: rating += 15
    if len(desc) > 250: rating += 10

    keywords = {
        "ai": 15,
        "saas": 15,
        "fintech": 15,
        "blockchain": 10,
        "automation": 10,
        "healthtech": 10,
        "edtech": 10,
    }

    for k, v in keywords.items():
        if k in desc:
            rating += v

    if "problem" in desc and "solution" in desc:
        rating += 15

    if len(name) >= 4: rating += 5
    if len(tagline) >= 10: rating += 5

    return min(max(rating, 0), 100)

# ---------- API ----------
@app.post("/submit-idea")
def submit_idea(idea: Idea):
    rating = calculate_rating(
        idea.name,
        idea.tagline,
        idea.description
    )

    # 🔥 STORE IN FIRESTORE
    db.collection("startup_ideas").add({
        "name": idea.name,
        "tagline": idea.tagline,
        "description": idea.description,
        "rating": rating,
        "votes": 0,
        "createdAt": datetime.utcnow(),
    })

    return {
        "success": True,
        "rating": rating,
        "message": "Idea stored in Firebase successfully"
    }
