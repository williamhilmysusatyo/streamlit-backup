import streamlit as st
import sqlite3
import pandas as pd
from student_name02 import load_student_names
from PIL import Image

def union(conn):
  cursor = conn.cursor()
  sql_query = '''
        WITH CombinedScores AS (
            SELECT
                A.studentName, A.studentID, B.courseName, A.assignmentID AS Tutorial, A.answerScore AS Score1, 0 AS Score2, 0 AS Score3
            FROM
                aes_student_answer_score AS A, aes_course AS B
            WHERE
                (A.courseID = B.courseID) AND (A.assignmentID = 1) 
            UNION
            SELECT
                A.studentName, A.studentID, B.courseName, A.assignmentID AS Tutorial, 0 AS Score1, A.answerScore AS Score2, 0 AS Score3
            FROM
                aes_student_answer_score AS A, aes_course AS B
            WHERE
                (A.courseID = B.courseID) AND (A.assignmentID = 2) 
            UNION
            SELECT
                A.studentName, A.studentID, B.courseName, A.assignmentID AS Tutorial, 0 AS Score1, 0 AS Score2, A.answerScore AS Score3
            FROM
                aes_student_answer_score AS A, aes_course AS B
            WHERE
                (A.courseID = B.courseID) AND (A.assignmentID = 3) 
        )
        SELECT
            studentName,
            studentID,
            courseName,
            Tutorial,
            Score1,
            Score2,
            Score3,
            (Score1 + Score2 + Score3) AS TotalScore
        FROM
            CombinedScores;
    '''

  cursor.execute(sql_query)
  result = cursor.fetchall()
  column_names = [desc[0] for desc in cursor.description]
  df_course = pd.DataFrame(result, columns=column_names)

  cursor.close()
  conn.close()

  return df_course

def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = st.checkbox("Checklist for Activated Filter", value=True)

    if not modify:
        return df

    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df[['courseName', 'Tutorial']].columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()
    # print(df[['Courses', 'Assignment']].columns)
    with modification_container:
        
        to_filter_columns = st.multiselect("Filter data", df[['courseName', 'Tutorial']].columns)
        for column in to_filter_columns:
            left, right = st.columns((14,1))
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = left.multiselect(
                    f"Select to {column}",
                    df[column].unique(),
                    default=[]
                    # list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = left.slider(
                    f"Select to {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = left.date_input(
                    f"Select to {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = left.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]

    return df
  
st.set_page_config(page_title="Page Title", layout="wide")
isi_file = ""

st.markdown("""
    <style>
        .block-container {
            #background-color: white;
            padding-top: 0.5rem;
            padding-bottom: 0rem;
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        body{ background-color: white;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)

head1 = st.header('Real Time Online Tutorial Test',  divider='rainbow')
head2 = st.write('**Open University** | :sunglasses: **:blue[Automatic Essay Scoring]**')
conn = sqlite3.connect('database_aes03.db')
student_names = load_student_names(conn)

with st.sidebar:
  image = Image.open('student.jpg')
  st.image(image)

tab1, tab2, tab3, tab4 = st.tabs(["Score", "Question", "Course", "Tutor/Lecturer"])
df_course = union(conn)
st.table(df_course)

with tab1:
  row1_col1,  row1_col2, row1_col3  = st.columns([3, 0.5, 11.5])
  
  with row1_col1:
    st.markdown('\n')
    x = filter_dataframe(df_course)
  with row1_col2:
            ()
  with row1_col3:
    st.markdown("""
    <style>
    .big-font {
        font-size:20px !important;
    }
    </style>
    """, unsafe_allow_html=True)
  
    st.markdown('<p class="big-font">Scoring Data </p>', unsafe_allow_html=True)
    
    st.dataframe(x, width=3000, height= 413)

  #add_identity = st.selectbox(
          #"Student Identity", student_names
      #)
  
  #table = union(conn, add_identity)
  #st.table(table)

with tab2:
 st.write('Tab 2')
  
with tab3:
  st.write('Tab 3')
  
with tab4:
  st.write('Tab 4')
  
