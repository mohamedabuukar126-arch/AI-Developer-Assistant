import sqlite3

def create_database():
    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY AUTOINCREMENT, user_message TEXT, ai_response TEXT)""")
    cursor.execute("CREATE TABLE IF NOT EXISTS memory( id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT, value TEXT, timestamp DATETIME)""")
    cursor.execute("CREATE TABLE IF NOT EXISTS chathistory (id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT, message TEXT)""") 
    cursor.execute("""CREATE TABLE IF NOT EXISTS memory (id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT UNIQUE, value TEXT, timestamp DATETIME)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT)""")
    cursor.execute("""INSERT OR IGNORE INTO settings(key, value) VALUES ('memory_enabled', 'true')""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS knowledge( id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, content TEXT)""")
    print("knowledge table created")

    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect("chat.db")


def show_tables():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    conn.close()

def save_memory(key, value):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO memory (key, value, timestamp) VALUES (?, ?, CURRENT_TIMESTAMP)""", (key, value))
    conn.commit()
    conn.close()
    print("Saved Into the Memory") 

def get_all_memories():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM memory")
    memories = cursor.fetchall()
    conn.close()
    return memories
    

def delete_memories():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM memory")
    conn.commit()
    conn.close()
    print("Memories have been Cleared")

def save_memory(key, value):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO memory (key,value, timestamp) VALUES (?, ?, CURRENT_TIMESTAMP) ON CONFLICT(key) DO UPDATE SET value = excluded.value""", (key, value))
    conn.commit()
    conn.close()
    print(f"Saved memory: {key} = {value}")

def save_chat(role, message):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chathistory (role, message) VALUES (?, ?) """, (role, message))
    conn.commit()
    conn.close()

def get_chat_history():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(""" SELECT role, message FROM chathistory ORDER BY id""")
    rows = cursor.fetchall()
    history = []
    for role, message in rows:
        history.append({
            "role": role,
            "content" : message
        })
    return history

def delete_chathistory():   
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""DELETE FROM chathistory""")
    conn.commit()
    conn.close()
    print("Chat history has been deleted")

def get_setting(key):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT value FROM settings where key = ?""",(key,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    return None

def update_settings(key, value):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO settings(key, value) VALUES (?, ?) ON CONFLICT (key) DO UPDATE SET value = excluded.value""", (key, value))
    conn.commit()
    conn.close()

def save_document(filename, content):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO knowledge(filename, content) VALUES (?, ?)""", (filename, content))
    conn.commit()
    print("Inserted ID:", cursor.lastrowid)
    cursor.execute("SELECT * FROM knowledge")
    print("After insert:", cursor.fetchall())
    conn.close()
    print("Upload has been saved")

def get_documents():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT filename, content FROM knowledge""")
    documents = cursor.fetchall()
    conn.close()
    return documents
















    






                   




    