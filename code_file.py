import os
from dotenv import load_dotenv
from graphdatascience import GraphDataScience

# Load environment variables from .env file
load_dotenv()

# Retrieve Neo4j connection details from environment variables
URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")
DB_NAME = os.getenv("NEO4J_DATABASE", "neo4j")

# Initialize the Graph Data Science client
gds = GraphDataScience(
    URI,
    auth=(USER, PASSWORD),
    database=DB_NAME
)


print("Connected to Neo4j GDS server version:", gds.version())
print("\nAvailable GDS algorithms (first few rows):")
print(gds.list().head())

# gds.close()

#Create a graph projection for the food web data

if gds.graph.exists("foodWebGraph").exists:
    gds.graph.drop("foodWebGraph")

# First projection for directed analyses (degree, betweenness, closeness, communities)
G, proj_result = gds.graph.project(
    "foodWebGraph",
    {
        "Taxa": {
            "properties": [
                "taxon_id"
            ]
        }
    },
    {
        "eaten_by": {
            "orientation": "NATURAL",   # direction stays Predator -> Prey
            "properties": [
                "latitude",
                "longitude"
                ]
        }
    }
)

print(f"Projected {G.node_count()} nodes and {G.relationship_count()} relationships for directed analyses.\n")

# Run directed analyses
# Degree centrality
degree_centrality = gds.degree.write(
    G, 
    writeProperty="degree"
)
print("Degree centrality computed and written to the graph as 'degree' property.\n")

# Betweenness centrality
betweenness_centrality = gds.betweenness.write(
    G, 
    writeProperty="betweenness"
)
print("Betweenness centrality computed and written to the graph as 'betweenness' property.\n")

# Closeness centrality
closeness_centrality = gds.closeness.write(
    G, 
    writeProperty="closeness"
)
print("Closeness centrality computed and written to the graph as 'closeness' property.\n")

# Using Louvain method for community detection
communities = gds.louvain.write(
    G,
    writeProperty="community"
)
print("Communities detected using Louvain method and written to the graph as 'community' property.\n")




# After calculating all metrics, retrieve and display them

# Create a query to get all metrics for each node
metrics_query = """
MATCH (n:Taxa)
RETURN n.taxon_id as taxon_id,
       n.degree as degree,
       n.betweenness as betweenness,
       n.closeness as closeness,
       n.community as community
ORDER BY n.betweenness DESC
LIMIT 10
"""

# Run the query and get results as a pandas DataFrame
metrics_df = gds.run_cypher(metrics_query)

print("\nTop 10 species by betweenness centrality:")
print(metrics_df)

# If you want to get statistics for each metric
print("\nMetric Statistics:")
stats_query = """
MATCH (n:Taxa)
RETURN 
    'Degree' as metric,
    min(n.degree) as min,
    max(n.degree) as max,
    avg(n.degree) as avg,
    count(n) as count
UNION
MATCH (n:Taxa)
RETURN 
    'Betweenness' as metric,
    min(n.betweenness) as min,
    max(n.betweenness) as max,
    avg(n.betweenness) as avg,
    count(n) as count
UNION
MATCH (n:Taxa)
RETURN 
    'Closeness' as metric,
    min(n.closeness) as min,
    max(n.closeness) as max,
    avg(n.closeness) as avg,
    count(n) as count
"""


stats_df = gds.run_cypher(stats_query)
print(stats_df)

# Get community statistics
community_stats_query = """
MATCH (n:Taxa)
WITH n.community as community, count(*) as size
RETURN 
    community,
    size
ORDER BY size DESC
"""

community_df = gds.run_cypher(community_stats_query)
print("\nTop 5 largest communities:")
print(community_df)


# Query with species names
detailed_metrics_query = """
MATCH (n:Taxa)
RETURN n.taxon_id as taxon_id,
       n.common_name as common_name,
       n.scientific_name as scientific_name,
       n.degree as degree,
       n.betweenness as betweenness,
       n.closeness as closeness,
       n.community as community
ORDER BY n.betweenness DESC
LIMIT 10
"""

detailed_df = gds.run_cypher(detailed_metrics_query)
print("\nTop 10 species with details:")
print(detailed_df)