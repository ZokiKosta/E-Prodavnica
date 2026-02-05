import sqlite3

# Connect to the database
conn = sqlite3.connect("app.db")
cursor = conn.cursor()

# Drop the table safely
cursor.execute("DROP TABLE IF EXISTS cart_items;")

# Commit changes and close connection
conn.commit()
conn.close()

print("cart_items table deleted successfully.")
