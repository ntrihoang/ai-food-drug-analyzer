import os
from dotenv import load_dotenv
import os
import joblib
import numpy as np
import pandas as pd
import streamlit as st

from sentence_transformers import SentenceTransformer

from database import (
    lookup_drug,
    lookup_food,
    search_existing_interaction,
    get_similar_explanation
)

# các path
RF_MODEL_PATH = os.getenv("RF_MODEL_PATH")
OHE_ENCODER_PATH = os.getenv("OHE_ENCODER_PATH")
SENTENCE_MODEL_PATH = os.getenv("SENTENCE_MODEL_PATH")

@st.cache_resource
def load_models():

    text_encoder = SentenceTransformer(SENTENCE_MODEL_PATH)

    ohe = joblib.load(OHE_ENCODER_PATH)

    model = joblib.load(RF_MODEL_PATH)

    return text_encoder, ohe, model

text_encoder, ohe, model = load_models()
# ==========================================================
# PART 8.1 - BUILD MODEL FEATURES( đầu vào cho mô hình)
# ==========================================================

def build_features(drug_class, food_name):
    """
    Chuẩn bị đặc trưng đầu vào cho Random Forest.
    """

    # ------------------------------------------------------
    # Synthetic Description
    # ------------------------------------------------------

    sentence = (
        f"Interaction between {drug_class} drugs "
        f"and {food_name}."
    )

    # ------------------------------------------------------
    # Semantic Embedding
    # ------------------------------------------------------

    X_text = text_encoder.encode(
        [sentence],
        convert_to_numpy=True
    )

    # ------------------------------------------------------
    # Tabular Feature
    # ------------------------------------------------------

    df_tabular = pd.DataFrame(
        [
            {
                "major_drug_class": drug_class,
                "food_name": food_name
            }
        ]
    )

    X_tabular = ohe.transform(df_tabular)

    X_tabular = X_tabular.toarray()

    # ------------------------------------------------------
    # Feature Fusion
    # ------------------------------------------------------

    X_final = np.hstack(
        [
            X_text,
            X_tabular
        ]
    )

    return X_final

# ==========================================================
# PART 8.2 - RANDOM FOREST PREDICTION
# ==========================================================

def predict(drug_class, food_name):
    """
    Dự đoán mức độ tương tác.
    """

    X = build_features(
        drug_class,
        food_name
    )

    prediction = model.predict(X)[0]

    probabilities = model.predict_proba(X)[0]

    confidence = probabilities.max()

    probability_dict = dict(

        zip(

            model.classes_,

            probabilities

        )

    )

    return {

        "prediction": prediction,

        "confidence": confidence,

        "probabilities": probability_dict

    }

# ==========================================================
# PART 9 - PREDICTION PIPELINE
# ==========================================================

def predict_interaction(drug_input, food_input):
    """
    Pipeline chính của hệ thống.

    Returns
    -------
    dict
        Kết quả trả về cho giao diện.
    """

    # ---------------------------------------------
    # Chuẩn hóa input
    # ---------------------------------------------
    drug_input = drug_input.strip()
    food_input = food_input.strip()

    # ---------------------------------------------
    # Tra cứu thuốc
    # ---------------------------------------------
    drug_info = lookup_drug(drug_input)

    if not drug_info:

        return {
            "status": "drug_not_found",
            "message": f"Drug '{drug_input}' was not found in the database."
        }

    # ---------------------------------------------
    # Tra cứu thực phẩm
    # ---------------------------------------------
    food_info = lookup_food(food_input)

    if not food_info:

        return {
            "status": "food_not_found",
            "message": f"Food '{food_input}' was not found in the database."
        }

    # ---------------------------------------------
    # Kiểm tra interaction đã tồn tại chưa
    # ---------------------------------------------
    interaction = search_existing_interaction(

        drug_info["drug_name"],
        food_info["food_name"]

    )

    if interaction:

        return {

            "status": "existing",

            "drug": drug_info,

            "food": food_info,

            "interaction": interaction

        }

    # ---------------------------------------------
    # AI Prediction
    # ---------------------------------------------
    prediction = predict(

        drug_info["drug_class"],

        food_info["food_name"]

    )

    # ---------------------------------------------
    # Explanation Retrieval
    # ---------------------------------------------
    explanation = get_similar_explanation(
        drug_info["drug_class"],
        food_info["food_name"],
        prediction["prediction"]

    )

    return {

        "status": "predicted",

        "drug": drug_info,

        "food": food_info,

        "prediction": prediction,

        "explanation": explanation

    }

print("Sentence model path:", SENTENCE_MODEL_PATH)