import streamlit as st
# Import the database functions from the new file
from database_connector import get_db_connection, submit_trivia_question, fetch_undispatched_trivia

# Set up the basic layout and title for your CMS portal
st.set_page_config(
    page_title="SportAura CMS Portal",
    layout="wide"
)

st.title("⚽ SportAura Admin Panel")
st.markdown("---")

# 1. Database Connection Check
conn = get_db_connection()
if not conn:
    # This error will show if the Streamlit secret is missing or incorrect
    st.error("Database connection failed. Please check Streamlit secrets and Supabase credentials.")
    st.stop()
else:
    # This success message will show when the connection is successful
    st.success("Database connected successfully! You can now submit trivia.")
    st.markdown("---")


# 2. New Trivia Dispatch Form
st.subheader("1. New Trivia Dispatch (Portal is Live!)")
with st.form("trivia_form"):
    question_text = st.text_area("Question Text:", placeholder="Enter the trivia question here...")
    correct_answer = st.text_input("Correct Answer:")
    option_2 = st.text_input("Option 2:")
    option_3 = st.text_input("Option 3:")
    
    submitted = st.form_submit_button("Queue Trivia Question")

    if submitted:
        if question_text and correct_answer and option_2 and option_3:
            if submit_trivia_question(conn, question_text, correct_answer, option_2, option_3):
                st.success("✅ Trivia question submitted successfully! Check the 'Undispatched Queue' below.")
            else:
                st.error("❌ Submission failed. Please check database configuration.")
        else:
            st.warning("Please fill in all four fields (Question, Correct Answer, Option 2, and Option 3).")

st.markdown("---")

# 3. Undispatched Queue Viewer (for verification)
st.subheader("2. Undispatched Trivia Queue")
st.markdown("Questions below are ready to be sent to the Telegram bot.")

# Fetch data and display
try:
    undispatched_data = fetch_undispatched_trivia(conn)
    if undispatched_data:
        # Prepare data for a clean display in a Streamlit dataframe
        display_data = []
        for item in undispatched_data:
            display_data.append({
                "ID": item['id'],
                "Question": item['question_text'],
                "Correct": item['correct_answer'],
                "Options": f"2: {item['option_2']}, 3: {item['option_3']}",
            })
        
        st.dataframe(display_data, use_container_width=True)
    else:
        st.info("The undispatched queue is empty! Great work.")
except NameError:
    st.warning("Could not fetch queue data due to database connection issues.")
