import sqlite3

# الاتصال بقاعدة البيانات
conn = sqlite3.connect('clinic.db')

# إنشاء كائن Cursor
cursor = conn.cursor()

# تنفيذ استعلام
cursor.execute("SELECT * FROM doctors")

# جلب البيانات
rows = cursor.fetchall()

for row in rows:
    print(row)

# إغلاق الاتصال
conn.close()
