
from kg_creation import KnowledgeGraph
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

def main():

    # connect to the database
    load_dotenv()

    URI = os.getenv("NEO4J_URI")
    USERNAME = os.getenv("NEO4J_USERNAME")
    PASSWORD = os.getenv("NEO4J_PASSWORD")

    AUTH = (USERNAME, PASSWORD)

    #creating driver forthe neo4j graph database
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        kg = KnowledgeGraph(driver)
        if kg.test_connection():
            print("Connection with graph database established")
        else:
            print("Error in connecting to graph database")


        airport_df = kg.load_airports("./sample_data/airports.dat")
        cleaned_airport_df = kg.clean_airports(airport_df)
        kg.create_airport_nodes(cleaned_airport_df)


        # Routes → edges  (airline_iata is an edge property, not a node)
        routes_df = kg.load_routes("./sample_data/routes.dat")
        print(routes_df.head())
        # cleaned_routes_df = kg.clean_routes(routes_df)
        # kg.create_route_edges(cleaned_routes_df)



# #next, we will try executing a smaple query on the knowledge graph
# query = ""
# kg.execute_query(query)

if __name__ == "__main__":
    main()