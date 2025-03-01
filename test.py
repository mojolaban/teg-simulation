from sqlalchemy import create_engine, text
import os

# Load the connection string from Replit environment variables
db_connection_string = os.environ['DB_CONNECTION_STRING']

# Create database engine
engine = create_engine(db_connection_string)

# Test connection
try:
    with engine.connect() as conn:
        result = conn.execute(text("SHOW DATABASES;"))
        print("✅ Connected to MySQL! Here are the available databases:")
        for row in result:
            print(row)
except Exception as e:
    print("❌ Failed to connect to MySQL:", e)
