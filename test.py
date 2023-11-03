import secrets

# Generate a random hexadecimal code with 16 characters (64 bits)
secret_code = secrets.token_hex(16)

print("Generated Secret Code:", secret_code)
# from pymongo import MongoClient

# # Initialize MongoDB client and database
# client = MongoClient("mongodb+srv://flaskdb:ypO42J2mw2N4NbY4@cluster0.axkqqxz.mongodb.net/?retryWrites=true&w=majority")
# # db = client.expense_tracker

# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)

