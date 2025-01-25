import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
from src.mcqGenerator.utils import read_file,get_table_data
from src.mcqGenerator.logger import logging
from langchain.callbacks import get_openai_callback
from src.mcqGenerator.MCQgenerator import generate_evaluate_chain
import streamlit as st

with open('Response.json', 'r') as file:
    RESPONSE_JSON = json.load(file)

st.title("MCQ Generator")

with st.form("user_inputs"):
    uploaded_file = st.file_uploader("Choose a file")

    mcq_count = st.number_input("Number of MCQs", min_value=1, max_value=20)

    subject = st.text_input("Subject")

    tone = st.selectbox("Tone", ["simple", "hard"])

    submit_button = st.form_submit_button("Generate MCQs")

    if submit_button & uploaded_file is not None & mcq_count is not None & subject is not None & tone is not None:
        with st.spinner("Generating MCQs..."):
            try:
                text = read_file(uploaded_file)
                with get_openai_callback() as cb:
                    response=generate_evaluate_chain(
                    {
                        "text": uploaded_file,
                        "number": mcq_count,
                        "subject":subject,
                        "tone": tone,
                        "response_json": RESPONSE_JSON
                    }
                    )
                st.write(response)
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                st.error("An error occurred while generating MCQs")
                logging.error(e)

            else:
                print(f"total tokens: {cb.total_tokens}")
                print(f"Prompt tokens: {cb.prompt_tokens}")
                print(f"Completion tokens: {cb.completion_tokens}")
                print(f"cost: {cb.total_cost}")
                if isinstance(response, dict):
                    quiz = response.get("quiz", None)
                    if quiz:
                        table = get_table_data(quiz)
                        if table:
                            df = pd.DataFrame(table)
                            df.index += 1
                            st.table(df)
                            st.text_area(label = "Review", value = response["review"])   
                        else:
                            st.error("An error occurred while generating MCQs")
                
                else:
                    st.write(response)
