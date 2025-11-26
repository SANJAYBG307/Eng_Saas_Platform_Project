import MySQLdb

conn = MySQLdb.connect(host='localhost', user='Saas_User', password='Saas@123', db='saas_platform')
cur = conn.cursor()

tables_to_check = ['tenants', 'roles', 'useraccount', 'departments', 'sections', 'subjects']

for table in tables_to_check:
    cur.execute(f"SHOW TABLES LIKE '{table}'")
    result = cur.fetchone()
    print(f"{table}: {'EXISTS' if result else 'MISSING'}")

conn.close()
