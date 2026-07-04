import sqlite3

import os

from dotenv import load_dotenv

from rapidfuzz import process

# load path 
load_dotenv()
DATABASE_PATH = os.getenv("DATABASE_PATH")

# hàm gợi ý tìm kiếm
def search_drug_names(keyword, limit=5):

    with sqlite3.connect(DATABASE_PATH) as conn:

        cursor = conn.cursor()

        query = """
        SELECT drug_name
        FROM Drugs
        WHERE LOWER(drug_name) LIKE LOWER(?)
        ORDER BY drug_name
        LIMIT ?
        """

        cursor.execute(
            query,
            (keyword.strip() + "%", limit)
        )

        return [row[0] for row in cursor.fetchall()]
def search_food_names(keyword, limit=5):

    with sqlite3.connect(DATABASE_PATH) as conn:

        cursor = conn.cursor()

        query = """
        SELECT food_name
        FROM Foods
        WHERE LOWER(food_name) LIKE LOWER(?)
        ORDER BY food_name
        LIMIT ?
        """

        cursor.execute(
            query,
            (keyword.strip() + "%", limit)
        )

        return [row[0] for row in cursor.fetchall()]
    
def lookup_drug(drug_name):
    """
    Tìm kiếm thuốc.
    Nếu không tìm thấy chính xác sẽ dùng Fuzzy Search.
    """
    with sqlite3.connect(DATABASE_PATH) as conn:

        cursor = conn.cursor()
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
    with sqlite3.connect(DATABASE_PATH) as conn:

        cursor = conn.cursor()
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
    with sqlite3.connect(DATABASE_PATH) as conn:

        cursor = conn.cursor()
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
    with sqlite3.connect(DATABASE_PATH) as conn:

        cursor = conn.cursor()
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
    with sqlite3.connect(DATABASE_PATH) as conn:

        cursor = conn.cursor()
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
