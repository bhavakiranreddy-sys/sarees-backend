import pymysql
try:
    conn = pymysql.connect(host='localhost', user='saree_user', password='saree_password', port=3306)
    print("Connected to 3306")
    conn.close()
except Exception as e:
    print(f"Failed to connect to 3306: {e}")

try:
    conn = pymysql.connect(host='localhost', user='saree_user', password='saree_password', port=3307)
    print("Connected to 3307")
    conn.close()
except Exception as e:
    print(f"Failed to connect to 3307: {e}")
