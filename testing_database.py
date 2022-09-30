import psycopg2

import os
from dotenv import load_dotenv
import datetime
load_dotenv()

DB_URL = os.environ["DB_URL"]


conn = psycopg2.connect(DB_URL)
cursor = conn.cursor()



# cursor.execute("SELECT * FROM resources;")
# for r in cursor:
#     print(r)

# cursor.execute("SELECT * FROM users;")
# for r in cursor:
#     print(r)


# query = f"SELECT username FROM users WHERE users_id = 7;"
# cursor.execute(query)
# a = cursor.fetchone()
# try:
#     print (a[0])
# except:
#     print (-1)

# cursor.execute("SELECT * FROM courses;")
# for r in cursor:
#     print(r)

# cursor.execute("SELECT * FROM notes;")
# for r in cursor:
#     print(r)

# cursor.execute("SELECT url_link  FROM resources WHERE topic_name = 'Machine Learning';")
# for r in cursor:
#     print(r[0])

# cursor.execute("SELECT users_id  FROM users")
# for i in cursor:
# #     print(i)

# query = f"SELECT * FROM tasks WHERE assigned_to_id = 2"
# cursor.execute(query)
# a = cursor.fetchall()

# for s in a:
#     print(s)

# a = datetime.date(2020, 9, 2)
# s = datetime.date.today()
# print(type((a-s).days))


# s = f"UPDATE tasks SET completed = True WHERE task_id = 47619;"
# cursor.execute(s)
# conn.commit()


# cursor.execute("SELECT * FROM tasks;")
# for r in cursor:
#     print(r)


s = f"SELECT COUNT(task_id) FROM tasks WHERE assigned_to_id = 2 AND completed = True"
cursor.execute(s)
i = cursor.fetchone()
print(i)


if(conn):
    cursor.close()
    conn.close()
    print("PostgreSQL connection is closed")


