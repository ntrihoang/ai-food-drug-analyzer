# ==========================================================
# UI TRANSLATIONS
# ==========================================================

TEXT = {

    "en": {

        "title": "Drug - Food Interaction Prediction System",

        "intro": "This system predicts potential interactions between **drugs** and **foods** using a Hybrid Machine Learning model (**Sentence Transformer + Random Forest**).",

        "drug": "💊 Drug",

        "food": "🍎 Food",

        "predict": "Predict",

        "placeholder_drug": "Example: Warfarin",

        "placeholder_food": "Example: Spinach",

        "empty_input": "Please enter both Drug and Food.",

        "running": "Running AI prediction...",

        "clinical_evidence": "📚 Clinical Evidence (Found in Database)",

        "ai_prediction": "🤖 AI Prediction (No direct evidence found in database)",

        "drug_info": "Drug",

        "food_info": "Food",

        "severity": "Severity",

        "predicted_severity": "Predicted Severity",

        "confidence": "Confidence",

        "prediction_probability": "Prediction Probabilities",

        "description": "Clinical Description",

        "recommendation": "Safety Recommendation",

        "clinical_reference": "Clinical Reference",

        "matched_by": "Matched By",

        "reference_drug": "Reference Drug",

        "source": "Source",

        "no_reference": "No similar clinical explanation found."

    },

    "vi": {

        "title": "Hệ thống dự đoán tương tác thuốc và thực phẩm",

        "intro": "Hệ thống dự đoán các tương tác tiềm ẩn giữa **thuốc** và **thực phẩm** bằng mô hình Hybrid AI (**Sentence Transformer + Random Forest**).",

        "drug": "💊 Thuốc",

        "food": "🍎 Thực phẩm",

        "predict": "Dự đoán",

        "placeholder_drug": "Ví dụ: Warfarin",

        "placeholder_food": "Ví dụ: Spinach",

        "empty_input": "Vui lòng nhập tên thuốc và thực phẩm.",

        "running": "Đang chạy mô hình AI...",

        "clinical_evidence": "📚 Đã có bằng chứng lâm sàng",

        "ai_prediction": "🤖 AI dự đoán (Không tìm thấy dữ liệu trực tiếp trong cơ sở dữ liệu)",

        "drug_info": "Thuốc",

        "food_info": "Thực phẩm",

        "severity": "Mức độ",

        "predicted_severity": "Mức độ dự đoán",

        "confidence": "Độ tin cậy",

        "prediction_probability": "Xác suất dự đoán",

        "description": "Mô tả lâm sàng",

        "recommendation": "Khuyến nghị",

        "clinical_reference": "Tham khảo lâm sàng",

        "matched_by": "Khớp theo",

        "reference_drug": "Thuốc tham chiếu",

        "source": "Nguồn",

        "no_reference": "Không tìm thấy giải thích tương tự."

    }

}

SEVERITY = {

    "en": {

        "High": "High",

        "Moderate": "Moderate",

        "Low": "Low"

    },

    "vi": {

        "High": "Cao",

        "Moderate": "Trung bình",

        "Low": "Thấp"

    }

}

RECOMMENDATIONS = {

    "en": {

        "High": {
            "title": "🔴 High Risk",
            "items": [
                "Avoid taking the drug and food together.",
                "Consult your doctor or pharmacist before continuing.",
                "Monitor for unusual symptoms such as bleeding, dizziness, or rash."
            ]
        },

        "Moderate": {
            "title": "🟡 Moderate Risk",
            "items": [
                "You may need to adjust the timing of your medication and meals.",
                "Monitor your symptoms during use.",
                "Consult a healthcare professional if symptoms occur."
            ]
        },

        "Low": {
            "title": "🟢 Low Risk",
            "items": [
                "No significant interaction has been identified.",
                "Continue taking the medication as prescribed.",
                "Consult your doctor if you have underlying conditions."
            ]
        }

    },

    "vi": {

        "High": {
            "title": "🔴 Nguy cơ cao",
            "items": [
                "Không nên sử dụng thuốc và thực phẩm này cùng thời điểm.",
                "Liên hệ bác sĩ hoặc dược sĩ trước khi tiếp tục sử dụng.",
                "Theo dõi các dấu hiệu bất thường như chảy máu, chóng mặt hoặc phát ban."
            ]
        },

        "Moderate": {
            "title": "🟡 Nguy cơ trung bình",
            "items": [
                "Có thể cần điều chỉnh thời gian dùng thuốc và bữa ăn.",
                "Theo dõi triệu chứng trong quá trình sử dụng.",
                "Nếu xuất hiện dấu hiệu bất thường, hãy liên hệ nhân viên y tế."
            ]
        },

        "Low": {
            "title": "🟢 Nguy cơ thấp",
            "items": [
                "Chưa ghi nhận tương tác đáng kể trong dữ liệu hiện có.",
                "Tiếp tục sử dụng thuốc theo đúng chỉ định.",
                "Nếu có bệnh nền hoặc đang dùng nhiều thuốc khác, hãy hỏi ý kiến bác sĩ."
            ]
        }

    }

}