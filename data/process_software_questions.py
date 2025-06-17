import dotenv
import os
import pandas as pd
from pymongo import MongoClient

# Load the CSV file with proper encoding
csv_file = './Software Questions.csv'
df = pd.read_csv(csv_file, encoding='latin-1')

# Explore the dataset
print("Dataset Overview:")
print(df.head())
print("\nColumns:")
print(df.columns)
print("\nDataset Info:")
print(df.info())
print("\nDataset Description:")
print(df.describe())
print("\nDataset Shape:")
print(df.shape)

# Check for missing values
print("\nMissing Values:")
print(df.isnull().sum())

# Check unique categories and difficulties
print("\nUnique Categories:")
print(df['Category'].unique())
print("\nUnique Difficulties:")
print(df['Difficulty'].unique())

# load connection string from env file

# load env file
dotenv.load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv('MONGODB_URI'))

# Test connection
print("\nAvailable databases:")
print(client.list_database_names())

# Create new database for software questions
db = client['software_questions_db']
collection = db['questions']

# Convert DataFrame to list of dictionaries
df_list = df.to_dict(orient='records')

# Insert data into MongoDB
result = collection.insert_many(df_list)
print(f"\nInserted {len(result.inserted_ids)} documents into MongoDB")

# Verify insertion
print(f"Total documents in collection: {collection.count_documents({})}")

# Show some sample documents
print("\nSample documents from MongoDB:")
for doc in collection.find().limit(3):
  print(doc)

# Close connection
client.close()
print("\nConnection closed successfully")
