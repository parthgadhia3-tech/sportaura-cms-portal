import streamlit as st
import psycopg2

@st.cache_resource
def get_db_connection():
    """
    Establishes and caches the database connection using explicit parameters
    and enforcing 'sslmode=require' for secure Supabase connections.
    """
    try:
        # Retrieve the individual parameters from secrets
        supabase_config = st.secrets["connections"]["supabase"]
        
        # Connect using individual, explicit keyword arguments, including sslmode
        conn = psycopg2.connect(
            host=supabase_config["host"],
            database=supabase_config["database"],
            user=supabase_config["user"],
            password=supabase_config["password"],
            port=supabase_config["port"],
            sslmode=supabase_config["sslmode"]
        )
        return conn
    except KeyError as e:
        # This handles if any of the 6 required keys (host, db, user, pass, port, sslmode) are missing from Streamlit secrets
        st.error(f"Configuration Error: Streamlit secrets is missing a required database key: {e}. Please ensure you have all 6 keys configured.")
        return None
    except Exception as e:
        # This handles general connection failures (like wrong password or temporary network issues)
        st.error(f"Error connecting to database: {e}")
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
