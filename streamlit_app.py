import streamlit as st



# Set up the basic layout and title for your CMS portal

st.set_page_config(

    page_title="SportAura CMS Portal",

    layout="wide"

)



st.title("⚽ SportAura Admin Panel")

st.markdown("---")



st.info("👋 This is your live Content Management System (CMS). Next, we will connect it to a database!")



# This form will be used to submit new trivia questions later

st.subheader("1. New Trivia Dispatch (Portal is Live!)")

with st.form("trivia_form"):

    st.text_area("Question Text:", placeholder="Enter the trivia question here...")

    st.text_input("Correct Answer:")

    st.text_input("Option 2:")

    st.text_input("Option 3:")

    st.form_submit_button("Queue Trivia to Telegram Bot (Not yet connected to DB)")
