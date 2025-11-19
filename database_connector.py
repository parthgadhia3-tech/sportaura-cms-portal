import streamlit as st
import psycopg2

@st.cache_resource
def get_db_connection():
    """
    Establishes and caches the database connection using the full DSN URL.
    This method often resolves hostname translation issues in deployment environments.
    """
    try:
        # Retrieve the single DSN URL from secrets
        supabase_dsn = st.secrets["connections"]["supabase"]["url"]
        
        # Connect using the DSN string
        conn = psycopg2.connect(supabase_dsn)
        return conn
    except KeyError as e:
        # This handles if the 'url' key is missing from Streamlit secrets
        st.error(f"Configuration Error: Streamlit secrets is missing the required database key 'url': {e}. Please ensure you have configured the DSN URL.")
        return None
    except Exception as e:
        # This handles general connection failures
        st.error(f"Error connecting to database via DSN URL: {e}")
        return None

def submit_trivia_question(conn, question_text, correct_answer, option_2, option_3):
    """Inserts a new trivia question into the 'trivia' table."""
    if not conn:
        return False
    
    cursor = conn.cursor()
    sql = """
    INSERT INTO trivia (question_text, correct_answer, option_2, option_3, is_dispatched)
    VALUES (%s, %s, %s, %s, FALSE)
    """
    try:
        cursor.execute(sql, (question_text, correct_answer, option_2, option_3))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error submitting data: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def fetch_undispatched_trivia(conn):
    """Fetches trivia questions that have not yet been dispatched."""
    if not conn:
        return []

    cursor = conn.cursor()
    sql = """
    SELECT id, question_text, correct_answer, option_2, option_3
    FROM trivia
    WHERE is_dispatched = FALSE
    ORDER BY created_at DESC
    """
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        data_list = [dict(zip(column_names, row)) for row in results]
        return data_list
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return []
    finally:
        cursor.close()
