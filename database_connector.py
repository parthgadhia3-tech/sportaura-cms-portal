import streamlit as st
import psycopg2

@st.cache_resource
def get_db_connection():
    """Establishes and caches the database connection using Streamlit Secrets."""
    try:
        conn = psycopg2.connect(**st.secrets["connections"]["supabase"])
        return conn
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return None

def submit_trivia_question(conn, question_text, correct_answer, option_2, option_3):
    """Inserts a new trivia question into the 'trivia' table."""
    if not conn:
        return False
    
    # We will use a cursor to execute SQL commands
    cursor = conn.cursor()
    
    # SQL query to insert data
    sql = """
    INSERT INTO trivia (question_text, correct_answer, option_2, option_3, is_dispatched)
    VALUES (%s, %s, %s, %s, FALSE)
    """
    
    try:
        # Execute the query with the submitted form data
        cursor.execute(sql, (question_text, correct_answer, option_2, option_3))
        # Commit the transaction to make the changes permanent
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error submitting data: {e}")
        # Rollback the transaction in case of an error
        conn.rollback()
        return False
    finally:
        cursor.close()

def fetch_undispatched_trivia(conn):
    """Fetches trivia questions that have not yet been dispatched."""
    if not conn:
        return []

    cursor = conn.cursor()
    
    # SQL query to select all undispatched trivia
    sql = """
    SELECT id, question_text, correct_answer, option_2, option_3
    FROM trivia
    WHERE is_dispatched = FALSE
    ORDER BY created_at DESC
    """
    
    try:
        cursor.execute(sql)
        # Fetch all results
        results = cursor.fetchall()
        # Get column names for easier data access
        column_names = [desc[0] for desc in cursor.description]
        
        # Combine column names and rows into a list of dictionaries
        data_list = [dict(zip(column_names, row)) for row in results]
        return data_list
        
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return []
    finally:
        cursor.close()
