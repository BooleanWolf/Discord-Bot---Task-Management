import discord 
import requests
import os
from dotenv import load_dotenv
import psycopg2
import random 
from datetime import date, datetime

load_dotenv()
DB_URL = os.environ["DB_URL"]
conn = None 

conn = psycopg2.connect(DB_URL)
cursor = conn.cursor()

TOKEN = os.environ['TOKEN']


client = discord.Client(intents=discord.Intents.all())



###################################### user defined function ##################################################

def unique_id(table):
    tab = ''
    existing_ids = []
    if table == 'users':
        tab = 'users_id'
    elif table == 'courses':
        tab = 'course_id'
    elif table == 'notes':
        tab = 'notes_id'
    elif table == 'targets':
        tab = 'target_id'
    elif table == 'tasks':
        tab = 'task_id'

    query = f"SELECT {tab} FROM {table};"
    cursor.execute(query)
    for i in cursor:
        existing_ids.append(i[0])
    
    while True:
        uni_id = random.randint(1, 100000)
        if uni_id not in existing_ids:
            return uni_id


def find_the_id_of_a_user(username):
    query = f"SELECT users_id FROM users WHERE username = '{username}';"
    cursor.execute(query)
    a = cursor.fetchone()
    try:
        return a[0]
    except:
        return -1

def find_the_user_of_an_id(users_id):
    query = f"SELECT username FROM users WHERE users_id = '{users_id}';"
    cursor.execute(query)
    a = cursor.fetchone()
    try:
        return a[0]
    except:
        return -1

# For Resource Finding 
def add_resources(topic_name, url_link):
    props = "(topic_name, url_link)"
    values =  f"('{topic_name}', '{url_link}')"
    query = f"INSERT INTO resources {props} VALUES {values}"
    cursor.execute(query)
    conn.commit()

def show_resources():
    l = []
    cursor.execute("SELECT * FROM resources;")
    all = cursor.fetchall()
    for r in all:
        l.append({
            'Name' : r[0],
            'Link' : r[1]
        })

    return l


def find_resources(tag):
    l = []
    query = f"SELECT url_link  FROM resources WHERE topic_name = '{tag}';"
    cursor.execute(query)
    for r in cursor:
        l.append(r[0])
    
    return l

#Registering User

def register_user(username, roles, total_task, total_target, completed_task, completed_target):

    query1 = f"SELECT username FROM users WHERE EXISTS (SELECT username FROM users WHERE username = '{username}');"

    cursor.execute(query1)
    j = 0
    for i in cursor:
        j += 1

    if j > 0:
        return 0

    users_id = unique_id('users')
    
    props = "(users_id, username, roles, total_task, total_target, completed_task, completed_target)"
    values =  f"('{users_id}', '{username}', '{roles}', {total_task}, {total_target}, {completed_task}, '{completed_target}')"
    query = f"INSERT INTO users {props} VALUES {values}"
    cursor.execute(query)
    conn.commit() 

    return 1

def show_users():
    l = []
    cursor.execute("SELECT * FROM users;")
    all = cursor.fetchall()
    for r in all:
        s = 0
        try:
            s = (r[5]/r[3])*100
        except:
            s = 0

        l.append({
            'ID' : r[0],
            'ign' : r[1],
            'Role' : r[2], 
            'Progress Weekly' : s, 
            'Overall Progress' : '0%'
        })

    return l

# Tasks 

def create_task(task_name, assigned_to, deadline):
    task_id = unique_id('tasks')
    description = 'None'
    completed = False 
    assigned_to_id = find_the_id_of_a_user(assigned_to)

    if assigned_to_id == -1:
        return -1
    

    props = "(task_id, deadline, task_name, description ,assigned_to_id, completed)"
    values =  f"('{task_id}', '{deadline}', '{task_name}','{description}','{assigned_to_id}','{completed}');"
    query = f"INSERT INTO tasks {props} VALUES {values}"
    cursor.execute(query)
    conn.commit()
    return 1

def show_task(username):
    users_id = find_the_id_of_a_user(username)

    if users_id == -1:
        return -1
    
    t = []

    query = f"SELECT * FROM tasks WHERE assigned_to_id = {users_id}"
    cursor.execute(query)
    a = cursor.fetchall()

    for s in a:
        deadline = s[1]
        days_left = 0
        Done = ""
        d = deadline.strftime("%d/%m/%y") 
        if s[5]:
            Done = "YES"
        else:
            Done = "No"
        
        days_left = deadline - date.today()
        days_left = days_left.days

        if days_left > 0:
            days_left = days_left 
        elif days_left == 0:
            days_left = "Ajkei last date!!!!!"
        else:
            days_left = "Deadline OVER!!!"

        t.append({
            'Task Name' : s[2], 
            'Deadline' : d, 
            'Completed' : Done, 
            'Status': days_left,
            'Task ID' : s[0]
        })

    return t

def done_task(task_id):
    try:
        s = f"UPDATE tasks SET completed = True WHERE task_id = {task_id};"
        cursor.execute(s)
        conn.commit()

        return 1
    except:
        return -1
     
# Update 
def update(username):
    users_id = find_the_id_of_a_user(username)
    s = f"SELECT COUNT(task_id) FROM tasks WHERE assigned_to_id = {users_id}"
    cursor.execute(s)
    task_assigned = cursor.fetchone()
    task_assigned = task_assigned[0]

    s = f"SELECT COUNT(task_id) FROM tasks WHERE assigned_to_id = {users_id} AND completed = True"
    cursor.execute(s)
    task_completed = cursor.fetchone()
    task_completed = task_completed[0]

    s = f"UPDATE users SET total_task = {task_assigned}, completed_task = {task_completed} WHERE users_id = {users_id}"
    cursor.execute(s)
    conn.commit()

    return 1


############################################################################################################################

@client.event
async def on_ready():
    pass 


@client.event
async def on_message(message):
    msg = message.content

    if msg.startswith("$Hello"):
        user = message.author 
        await message.channel.send(f"Hello {user}.")
    
    if msg.startswith("$add_resources"):
        rest = msg.replace("$add_resources", '')
        rest = rest.split('>')
        topic_name = rest[0].strip()
        url_link =rest[1].strip()

        add_resources(topic_name, url_link)
    
    if msg.startswith("$show_all_resources"):
        l = show_resources()
        s = ''
        for r in range(len(l)):
            s += f"__Topic Name__ : {l[r]['Name']}\n__Link__ : {l[r]['Link']}\n======\n"
        
        await message.channel.send(s)
        

    if msg.startswith("$show_resource"):

        rest = msg.replace("$show_resource", '')
        rest = rest.strip()

        l = find_resources(rest)
        s = ''
        s += "Possible Links you are looking for are\n"
        for r in range(len(l)):
            s += f"{r+1}. {l[r]}\n--\n"
   
        
        await message.channel.send(s)

    if msg.startswith("$register"):
        username = message.author 
        roles = 'None'
        total_task = 0
        total_target = 0
        completed_task = 0
        completed_target = 'ABCABCABC'

        a = register_user(username, roles, total_task, total_target, completed_task, completed_target)
        if a == 1:
            await message.channel.send(f"{username} has been registered succesfully") 
        else:
            await message.channel.send(f"Kotobar ar registeted hoba bondhu. ekbar hoyecho already")

    
    if msg.startswith("$show_users"):
        a = show_users()
        s = ''
        s += "***The Users are***\n"
        for r in range(len(a)):
            s += f"ID: {a[r]['ID']}\nUserName: {a[r]['ign']}\nRole: {a[r]['Role']}\nWeekly Progress: {a[r]['Progress Weekly']}%\n---\n"

        await message.channel.send(s)

    if msg.startswith("$set_task"):
        rest = msg.replace("$set_task", '')
        rest = rest.strip()
        rest = rest.split('>')
        task_name = rest[0].strip()
        assigned_to = rest[1].strip()
        deadline = rest[2].strip()
        deadline = datetime.strptime(deadline, '%d/%m/%Y').date() 

        a = create_task(task_name, assigned_to, deadline)
        if a ==1 :
            await message.channel.send("Task Added")
        elif a == -1:
            await message.channel.send("That user doesn't exist")
    
    if msg.startswith("$show_task"):
        rest = msg.replace("$show_task", '')
        rest = rest.strip()

        q = show_task(rest)

        if q==-1:
            await message.channel.send("jar task dekhte chasso tar kono kaj nai")
            return 
        s = ''
        s += f"\n\n***Task for {rest} are:-***\n"
        for i in range(len(q)):
            s += f"*Task Id:* {q[i]['Task ID']} --> __Task Name__ : {q[i]['Task Name']} \t __Deadline__ : {q[i]['Deadline']}\t __Status__ : {q[i]['Status']} Days left \t __Completed__ : {q[i]['Completed']}\n---\n"
        
        await message.channel.send(s)

    if msg.startswith("$done_task"):
        rest = msg.replace("$done_task", '')
        rest = rest.split('>')
        username = rest[0].strip()
        task_id = rest[1].strip()

        a = done_task(task_id)

        if a == 1:
            await message.channel.send("Your task has been set to completed")
        elif a == -1:
            await message.channel.send("Check your task id. That task doesn't exist")
    
    if msg.startswith("$update"):
        rest = msg.replace("$update", '')
        rest = rest.strip()
        username = rest 

        a = update(username)

        if a:
            await message.channel.send("Updated Succesfully")

    


client.run(TOKEN)


if(conn):
    cursor.close()
    conn.close()
    print("PostgreSQL connection is closed")


