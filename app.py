import streamlit as st
from dotenv import load_dotenv

from predictor import predict_interaction
from resources import TEXT, SEVERITY, RECOMMENDATIONS

from database import search_drug_names,search_food_names
# ==========================================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================================

load_dotenv()

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Drug-Food Interaction Prediction",
    page_icon="💊",
    layout="centered"
)

# ==========================================================
# HEADER
# ==========================================================
language = st.sidebar.selectbox(

    "🌐 Language",

    ["English", "Tiếng Việt"]

)

lang = "vi" if language == "Tiếng Việt" else "en"

t = TEXT[lang]


st.title(t["title"])

st.markdown(t["intro"])

st.divider()

# ==========================================================
# USER INPUT
# ==========================================================

drug = st.text_input(
    t["drug"],
    placeholder=t["placeholder_drug"]
)
selected_drug = None

if len(drug.strip()) >= 2:

    suggestions = search_drug_names(drug)

    if suggestions:

        selected_drug = st.selectbox(
            "Gợi ý tên thuốc" if lang=='vi' else "drug_suggestions",
            [""] + suggestions
        )
food = st.text_input(
    t["food"],
    placeholder=t["placeholder_food"]
)

selected_food = None

if len(food.strip()) >= 2:

    suggestions = search_food_names(food)

    if suggestions:

        selected_food = st.selectbox(
            "Gợi ý tên thực phẩm" if lang=='vi' else "food_suggestions",
            [""] + suggestions
        )


predict_btn = st.button(
    t["predict"],
    use_container_width=True
)

# ==========================================================
# PREDICTION
# ==========================================================

if predict_btn:

    if drug.strip() == "" or food.strip() == "":

        st.warning(t["empty_input"])

    else:

        with st.spinner(t["running"]):

            drug_input = selected_drug if selected_drug else drug

            result = predict_interaction(
                drug_input,
                food
            )

        # ==================================================
        # EXISTING INTERACTION
        # ==================================================

        if result["status"] == "existing":

            st.success(t["clinical_evidence"])

            st.divider()

            col1, col2 = st.columns(2)

            with col1:

                st.subheader(t["drug"])

                st.write(result["drug"]["drug_name"])

                st.caption(result["drug"]["drug_class"])

            with col2:

                st.subheader(t["food"])

                st.write(result["food"]["food_name"])

            st.divider()
            severity = result["interaction"]["severity"].title()
            severity_text = SEVERITY[lang][severity]

            if severity == "High":

                st.error(
                    f"{t['severity']} : {severity_text}"
                )

            elif severity == "Moderate":

                st.warning(
                    f"{t['severity']} : {severity_text}"
                )

            else:

                st.success(
                    f"{t['severity']} : {severity_text}"
                )
            

            st.subheader(t["recommendation"])

            recommendation = RECOMMENDATIONS[lang][severity]

            st.markdown(
                recommendation["title"]
            )

            for item in recommendation["items"]:

                st.markdown(f"- {item}")

            st.divider()
            st.subheader(t["description"])

            st.write(result["interaction"]["description"])
            

            with st.expander(t["source"]):

                st.write(result["interaction"]["source"])

        # ==================================================
        # AI PREDICTION
        # ==================================================

        elif result["status"] == "predicted":

            prediction = result["prediction"]

            st.info(
            t["ai_prediction"]
            )

            st.divider()

            col1, col2 = st.columns(2)

            with col1:

                st.subheader(t["drug"])

                st.write(result["drug"]["drug_name"])

                st.caption(result["drug"]["drug_class"])

            with col2:

                st.subheader(t["food"])

                st.write(result["food"]["food_name"])

            st.divider()

            severity = prediction["prediction"].title()

            severity_text = SEVERITY[lang][severity]

            if severity == "High":

                st.error(
                    f"{t['severity']} : {severity_text}"
                )

            elif severity == "Moderate":

                st.warning(
                    f"{t['severity']} : {severity_text}"
                )

            else:

                st.success(
                    f"{t['severity']} : {severity_text}"
                )

            st.metric(

                label=t["confidence"],

                value=f"{prediction['confidence']:.2%}"

            )

            st.subheader(
            t["prediction_probability"]
            )

            for cls, prob in prediction["probabilities"].items():

                display_cls = SEVERITY[lang][cls]

                st.write(f"**{display_cls}**")

                st.progress(float(prob))

                st.caption(f"{prob:.2%}")


            st.subheader(
                t["recommendation"]
            )

            recommendation = RECOMMENDATIONS[lang][severity]

            st.markdown(
                recommendation["title"]
            )

            for item in recommendation["items"]:

                st.markdown(f"- {item}")

            explanation = result["explanation"]

            if explanation:

                st.divider()

                st.subheader(
                t["clinical_reference"]
                )

                st.write(
                    f"**{t['matched_by']}:** {explanation['matched_by']}"
                )

                st.write(
                    f"**{t['reference_drug']}:** {explanation['reference_drug']}"
                )

                st.write(explanation["description"])

                with st.expander(t["source"]):

                    st.write(explanation["source"])

            else:

                st.info(t["no_reference"])
            st.divider()
        # ==================================================
        # ERROR
        # ==================================================

        else:

            st.error(result["message"])