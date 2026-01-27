from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from hf_utils import fetch_text_classification_models, get_model_metadata
from topsis_core import run_topsis_df

app = FastAPI(title="TOPSIS Model Selector")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------- Request Schema ---------
class TopsisRequest(BaseModel):
    models: list
    weights: dict


# --------- Routes ---------
@app.get("/")
def home():
    return {"message": "TOPSIS Model Selector Running"}


@app.get("/available-models")
def available_models():
    return fetch_text_classification_models(50)


@app.post("/rank-models")
def rank_models(req: TopsisRequest):

    # Enforce 4–5 model rule
    if not (4 <= len(req.models) <= 5):
        raise HTTPException(status_code=400, detail="Select 4–5 models only")

    # Fetch metadata
    meta = get_model_metadata(req.models)

    # Build decision matrix
    rows = []
    for model in req.models:
        data = meta[model]
        rows.append([
            model,
            data["accuracy"],
            data["latency"],
            data["size"],
            data["languages"]
        ])

    df = pd.DataFrame(
        rows,
        columns=[
            "Model",
            "Accuracy",
            "Latency",
            "Model Size",
            "Language Coverage"
        ]
    )

    # Run TOPSIS
    result = run_topsis_df(
        df,
        weights=[
            req.weights["accuracy"],
            req.weights["latency"],
            req.weights["size"],
            req.weights["languages"]
        ],
        impacts=["+", "-", "-", "+"]
    )

    return result.to_dict(orient="records")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "../frontend")),
    name="static"
)

@app.get("/")
def serve_frontend():
    return FileResponse(os.path.join(BASE_DIR, "../frontend/index.html"))