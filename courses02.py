
def load_courses(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT Course FROM course_info')
    return [row[0] for row in cursor.fetchall()]
