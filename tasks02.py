
def load_tasks(conn, course_name):
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT Task FROM course_info WHERE Course = ?', (course_name,))
    return [row[0] for row in cursor.fetchall()]
