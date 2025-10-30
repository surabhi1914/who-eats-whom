import os
from dotenv import load_dotenv
from graphdatascience import GraphDataScience

load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")
DB_NAME = os.getenv("NEO4J_DATABASE", "neo4j")

print("URI =", URI)
print("USER =", USER)
print("DB_NAME =", DB_NAME)
print("PASSWORD LENGTH =", len(PASSWORD) if PASSWORD else None)

gds = GraphDataScience(
    URI,
    auth=(USER, PASSWORD),
    database=DB_NAME
)

print("Connected to Neo4j GDS server version:", gds.version())

print("\nAvailable GDS algorithms (first few rows):")
print(gds.list().head())

gds.close()
