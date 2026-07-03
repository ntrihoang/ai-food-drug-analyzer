import sqlite3
import joblib
import pandas as pd
import numpy as np
from rapidfuzz import process
from sentence_transformers import SentenceTransformer
from scipy.sparse import hstack
# =====================================================
# PART 2 - CONFIGURATION
# =====================================================

DATABASE_PATH = "./data/database/drug-food-interaction.db"

RF_MODEL_PATH = "./models/hybrid_rf_model.pkl"

OHE_ENCODER_PATH = "./models/ohe_encoder.pkl"

SENTENCE_MODEL_PATH = "./models/sentence_transformer"

# ==========================================================
# PART 3 - LOAD AI COMPONENTS
# ==========================================================

print("=" * 60)
print("      DRUG - FOOD INTERACTION PREDICTION SYSTEM")
print("=" * 60)
print("Loading AI components...\n")

try:

    # Load Sentence Transformer
    print("[1/3] Loading Sentence Transformer...")
    text_encoder = SentenceTransformer(SENTENCE_MODEL_PATH)

    # Load One-Hot Encoder
    print("[2/3] Loading One-Hot Encoder...")
    ohe = joblib.load(OHE_ENCODER_PATH)

    # Load Random Forest
    print("[3/3] Loading Random Forest Model...")
    model = joblib.load(RF_MODEL_PATH)

    print("\nAll AI components loaded successfully!")

except Exception as e:

    print("\nFailed to load AI system.")
    print(e)

    exit()

# ==========================================================
# PART 4 - CONNECT SQLITE DATABASE
# ==========================================================

try:

    conn = sqlite3.connect(DATABASE_PATH)

    cursor = conn.cursor()

    print("Database connected successfully.\n")

except Exception as e:

    print("Cannot connect to database.")
    print(e)

    exit()

# ==========================================================
# PART 5 - DATABASE LOOKUP FUNCTIONS
# ==========================================================

def lookup_drug(drug_name):
    """
    Tìm kiếm thuốc.
    Nếu không tìm thấy chính xác sẽ dùng Fuzzy Search.
    """

    query = """
    SELECT
        drug_name,
        drug_class,
        standardized_ingredient
    FROM Drugs
    WHERE LOWER(drug_name)=LOWER(?)
    """

    cursor.execute(query, (drug_name.strip(),))

    row = cursor.fetchone()

    if row:

        return {
            "drug_name": row[0],
            "drug_class": row[1],
            "ingredient": row[2]
        }

    # Fuzzy Search
   
    suggestion = fuzzy_search(

        drug_name,

        "Drugs",

        "drug_name"

    )

    if suggestion:

        cursor.execute(query, (suggestion,))

        row = cursor.fetchone()

        return {

            "drug_name": row[0],

            "drug_class": row[1],

            "ingredient": row[2]

        }

    return None

def lookup_food(food_name):
    """
    Tìm kiếm thực phẩm.
    Nếu không có sẽ dùng fuzzy search.
    """

    query = """
    SELECT food_name
    FROM Foods
    WHERE LOWER(food_name)=LOWER(?)
    """

    cursor.execute(query, (food_name.strip(),))

    row = cursor.fetchone()

    if row:

        return {

            "food_name": row[0]

        }

    suggestion = fuzzy_search(

        food_name,

        "Foods",

        "food_name"

    )

    if suggestion:

        return {

            "food_name": suggestion

        }

    return None

def search_existing_interaction(drug_name, food_name):
    """
    Kiểm tra xem cặp thuốc - thực phẩm
    đã tồn tại trong database hay chưa.
    """

    query = """
        SELECT i.severity,

            i.description,

            i.source

        FROM Interactions i

        JOIN Drugs d

            ON i.drug_id=d.drug_id

        JOIN Foods f

            ON i.food_id=f.food_id

        WHERE

            LOWER(d.drug_name)=LOWER(?)

            AND

            LOWER(f.food_name)=LOWER(?)

        LIMIT 1
    """

    cursor.execute(

        query,

        (

            drug_name.strip(),

            food_name.strip()

        )

    )

    row = cursor.fetchone()

    if row:

        return {

            "severity": row[0],

            "description": row[1],

            "source": row[2]

        }

    return None

# ==========================================================
# PART 5.1 - FUZZY SEARCH
# ==========================================================

def fuzzy_search(keyword, table_name, column_name, score_cutoff=85):
    """
    Tìm kiếm gần đúng trong SQLite.

    Parameters
    ----------
    keyword : str
        Chuỗi người dùng nhập.

    table_name : str
        Tên bảng.

    column_name : str
        Tên cột cần tìm.

    score_cutoff : int
        Ngưỡng giống nhau (0-100).

    Returns
    -------
    str hoặc None
    """

    query = f"SELECT {column_name} FROM {table_name}"

    cursor.execute(query)

    values = [row[0] for row in cursor.fetchall()]

    if not values:
        return None

    match = process.extractOne(
        keyword,
        values,
        score_cutoff=score_cutoff
    )

    if match:

        return match[0]

    return None

# ==========================================================
# PART 7 - RETRIEVE SIMILAR EXPLANATION
# ==========================================================

def get_similar_explanation(drug_class, food_name, severity):
    """
    Tìm một interaction tương tự để giải thích.

    Ưu tiên:
        1. Cùng drug class + food
        2. Cùng food
    """

    # ------------------------------------------------------
    # Priority 1
    # Same Drug Class + Same Food
    # ------------------------------------------------------

    query = """
        SELECT

            d.drug_name,

            i.description,

            i.source

        FROM Interactions i

        JOIN Drugs d

            ON i.drug_id=d.drug_id

        JOIN Foods f

            ON i.food_id=f.food_id

        WHERE LOWER(d.drug_class)=LOWER(?)
        AND LOWER(f.food_name)=LOWER(?)
        AND i.severity = ?

        LIMIT 1
    """

    cursor.execute(
        query,
        (
            drug_class,
            food_name,
            severity
        )

    )

    row = cursor.fetchone()

    if row:

        return {

            "matched_by": "Drug Class + Food",

            "reference_drug": row[0],

            "description": row[1],

            "source": row[2]

        }

    # ------------------------------------------------------
    # Priority 2
    # Same Food
    # ------------------------------------------------------

    query = """
        SELECT

            d.drug_name,

            i.description,

            i.source

        FROM Interactions i

        JOIN Drugs d

            ON i.drug_id=d.drug_id

        JOIN Foods f

            ON i.food_id=f.food_id

        WHERE

            LOWER(f.food_name)=LOWER(?) AND i.severity=(?)

        LIMIT 1
    """

    cursor.execute(

        query,

        (

            food_name,severity

        )

    )

    row = cursor.fetchone()

    if row:

        return {

            "matched_by": "Food",

            "reference_drug": row[0],

            "description": row[1],

            "source": row[2]

        }

    return None

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

# ==========================================================
# PART 10 - DISPLAY FUNCTIONS
# ==========================================================

def show_database_result(result):
    """
    Hiển thị interaction có sẵn trong database.
    """

    print("\n" + "="*60)
    print("INTERACTION FOUND IN DATABASE")
    print("="*60)

    print(f"Drug        : {result['drug']['drug_name']}")
    print(f"Drug Class  : {result['drug']['drug_class']}")
    print(f"Food        : {result['food']['food_name']}")

    print("-"*60)

    print(f"Severity    : {result['interaction']['severity']}")

    print("\nDescription")
    print(result["interaction"]["description"])

    print("\nSource")
    print(result["interaction"]["source"])

    print("="*60)

def show_prediction_result(result):
    """
    Hiển thị kết quả AI Prediction.
    """

    prediction = result["prediction"]

    print("\n" + "="*60)
    print("AI PREDICTION")
    print("="*60)

    print(f"Drug        : {result['drug']['drug_name']}")
    print(f"Drug Class  : {result['drug']['drug_class']}")
    print(f"Food        : {result['food']['food_name']}")

    print("-"*60)

    print(f"Predicted Severity : {prediction['prediction']}")

    print(f"Confidence         : {prediction['confidence']:.2%}")

    print("\nClass Probabilities")

    for cls, prob in prediction["probabilities"].items():

        print(f"{cls:<10}: {prob:.2%}")

    explanation = result["explanation"]

    if explanation:

        print("\n" + "-"*60)

        print("Clinical Reference")

        print("-"*60)

        print(f"Matched By : {explanation['matched_by']}")

        print(f"Reference Drug : {explanation['reference_drug']}")

        print()

        print(explanation["description"])

        print()

        print(f"Source : {explanation['source']}")

    else:

        print("\nNo similar clinical explanation found.")

    print("="*60)

def show_error(message):

    print("\n" + "="*60)

    print("ERROR")

    print("="*60)

    print(message)

    print("="*60)

def main():

    while True:

        print()

        drug = input("Drug (q to quit): ")

        if drug.lower() == "q":
            break

        food = input("Food (q to quit): ")

        if food.lower() == "q":
            break

        result = predict_interaction(
            drug,
            food
        )

        if result["status"] == "existing":

            show_database_result(result)

        elif result["status"] == "predicted":

            show_prediction_result(result)

        else:

            show_error(result["message"])

    conn.close()

    print("\nGoodbye!")

if __name__ == "__main__":
    main()