import MySQLdb

# Drop and recreate database
conn = MySQLdb.connect(host='localhost', user='Saas_User', password='Saas@123')
cur = conn.cursor()

try:
    cur.execute("DROP DATABASE IF EXISTS saas_platform")
    print("Dropped database saas_platform")
    
    cur.execute("CREATE DATABASE saas_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    print("Created database saas_platform")
    
    conn.commit()
    print("Database reset successfully!")
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
