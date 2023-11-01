
def load_student_names(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT studentName FROM aes_student')
    return [row[0] for row in cursor.fetchall()]
