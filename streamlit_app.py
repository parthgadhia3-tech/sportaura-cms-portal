import streamlit as st
from supabase_client import get_supabase

st.title("Sportaura CMS")

supabase = get_supabase()

st.header("Add trivia question")
question = st.text_area("Question")
correct = st.text_input("Correct answer")
opt2 = st.text_input("Option 2")
opt3 = st.text_input("Option 3")
dispatched = st.checkbox("Is dispatched?", False)

if st.button("Add to Supabase"):
    if question and correct:
        supabase.table("trivia").insert({
            "question_text": question,
            "correct_answer": correct,
            "option_2": opt2,
            "option_3": opt3,
            "is_dispatched": dispatched
        }).execute()
        st.success("Inserted!")
    else:
        st.error("Question & correct answer required")

st.header("Existing Questions")
data = supabase.table("trivia").select("*").execute()
st.write(data.data)
