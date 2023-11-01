import streamlit as st
import sqlite3
import pandas as pd

def union(conn, student):
  cursor = conn.cursor()
  sql_query = '''
        WITH CombinedScores AS (
            SELECT
                A.studentName, A.studentID, B.courseName, A.assignmentID AS Tutorial, A.answerScore AS Score1, 0 AS Score2, 0 AS Score3
            FROM
                aes_student_answer_score AS A, aes_course AS B
            WHERE
                (A.courseID = B.courseID) AND (A.assignmentID = 1) AND A.studentName == ?
            UNION
            SELECT
                A.studentName, A.studentID, B.courseName, A.assignmentID AS Tutorial, 0 AS Score1, A.answerScore AS Score2, 0 AS Score3
            FROM
                aes_student_answer_score AS A, aes_course AS B
            WHERE
                (A.courseID = B.courseID) AND (A.assignmentID = 2) AND A.studentName == ?
            UNION
            SELECT
                A.studentName, A.studentID, B.courseName, A.assignmentID AS Tutorial, 0 AS Score1, 0 AS Score2, A.answerScore AS Score3
            FROM
                aes_student_answer_score AS A, aes_course AS B
            WHERE
                (A.courseID = B.courseID) AND (A.assignmentID = 3) AND A.studentName == ?
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

  cursor.execute(sql_query, (student, student, student))
  result = cursor.fetchall()
  column_names = [desc[0] for desc in cursor.description]
  df_course = pd.DataFrame(result, columns=column_names)

  cursor.close()
  conn.close()

  return df_course

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

with st.sidebar:
    conn = sqlite3.connect('database_aes03.db')
    student_names = load_student_names(conn)

    image = Image.open('student.jpg')
    st.image(image)

    add_identity = st.sidebar.selectbox(
        "Student Identity", student_names
    )

table = union(add_identity)
st.table(table)
