from database import session
from models import User
import sqlite3
import os

# # Connect to the database
# conn = sqlite3.connect("app.db")
# cursor = conn.cursor()
#
# # Drop the table safely
# cursor.execute("DROP TABLE IF EXISTS cart_items;")
#
# # Commit changes and close connection
# conn.commit()
# conn.close()
#
# print("cart_items table deleted successfully.")

# import sqlite3
# import os

# # Connect to the database
# conn = sqlite3.connect("app.db")
# cursor = conn.cursor()
#
# print(os.path.abspath("app.db"))
#
# # Optional: Drop existing users table if you want a clean reset
# cursor.execute("DROP TABLE IF EXISTS users;")
#
# # Create users table (aligned with SQLAlchemy model)
# cursor.execute("""
# CREATE TABLE users (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     username TEXT UNIQUE NOT NULL,
#     email TEXT UNIQUE NOT NULL,
#     password TEXT NOT NULL,
#     verified BOOLEAN NOT NULL DEFAULT 0,
#     verification_code TEXT NOT NULL,
#     is_admin BOOLEAN NOT NULL DEFAULT 0
# );
# """)
#
# # Commit changes and close connection
# conn.commit()
# conn.close()
#
# print("users table created successfully.")

# user = session.query(User).filter_by(username="zoki").first()
# user.is_admin = True
# session.commit()


conn = sqlite3.connect("app.db")
cursor = conn.cursor()

# Drop the table safely
# cursor.execute("""
#     INSERT INTO users (
#         username,
#         email,
#         password,
#         verification_code
#     ) VALUES (?, ?, ?, ?)
# """, (
#     "user2",
#     "user2@example.com",
#     "872e4bdc4edc15af0f49ca3746a867370207c5a7498017a94a2f7094c77a89e4",
#     "12345"
# ))

# cursor.execute("""
#     UPDATE users
#     SET is_admin = ?, verified = ?
#     WHERE username = ?
# """, (
#     1,
#     1,
#     "admin"
# ))

# cursor.execute("""
#     UPDATE users
#     SET password = $2b$12$h3C3sV6yQLB1/gcNxSJ.MeBlEPA54W4neyE5t6rDtXOKN56vN6Ft., verified = 1, is_admin = 1
#     WHERE username = admin
# """, (
#     hashed_password,
#     1,          # verified = true
#     1,          # is_admin = true
#     "admin"
# ))

# cursor.execute("""
#     UPDATE users
#     SET verified = ?
#     WHERE username = ?
# """, (
#     1,
#     "user1"
# ))

# Commit changes and close connection
conn.commit()
conn.close()



# import bcrypt
#
# password = "zoran124"
#
# hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
# print(hashed.decode())