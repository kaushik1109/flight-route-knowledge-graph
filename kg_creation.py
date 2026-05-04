from neo4j import GraphDatabase
import pandas as pd

class KnowledgeGraph:

    def __init__(self, driver):
        # initialize the driver for graph database and pass it to the required functions
        self.driver = driver

    def test_connection(self):
        result = self.driver.execute_query("RETURN 1 as num")
        return result
    
    def execute_query(self, query):
        pass

    def close_connection(self):
        self.driver.close()


############# AIRPORT NODES #############

    def load_airports(self, airport_file_path):
        airport_df = pd.read_csv(airport_file_path, header = None)
        print(airport_df.head)
        return airport_df
    
    #  we introduce functions to clean the data 
    def clean_airports(self, df):
        df = df[[1,2,3,4,5,6,7]].copy()

        df.columns = ["name", "city", "country", "iata", "icao", "lat", "lon"]

        # remove rows where iata is missing
        df = df[df["iata"] != "\\N"]

        #drop duplicates
        df = df.drop_duplicates(subset="iata")

        df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
        df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
        df = df.dropna(subset=["lat", "lon"])
 
        df = df.drop_duplicates(subset="iata").reset_index(drop=True)

        print(df.head())
        print(f"[airports] {len(df)} rows after cleaning")

        return df
    
    def create_airport_nodes(self, df):
        query = """
        MERGE (a:Airport {iata: $iata})
        SET a.name = $name,
            a.city = $city,
            a.country = $country,
            a.lat = $lat,
            a.lon = $lon
        """

        for _, row in df.iterrows():
            self.driver.execute_query(
                query,
                iata=row["iata"],
                name=row["name"],
                city=row["city"],
                country=row["country"],
                icao=row["icao"],
                lat=float(row["lat"]),
                lon=float(row["lon"])
            )
        print(f"[airports] {len(df)} nodes upserted")

############# ROUTE RELATIONSHIPS #############

    def load_routes(self, route_file_path):
        routes_df = pd.read_csv(route_file_path, header = None)
        print(type(routes_df))
    
    def clean_routes(self, routes_df):
        routes_df = routes_df[[0, 2, 4, 6, 7, 8]]

        routes_df.columns = [
        "airline_iata",
        "src_iata",
        "dst_iata",
        "codeshare",
        "stops",
        "equipment"
        ]

        for col in ["airline_iata", "src_iata", "dst_iata"]:
            routes_df = routes_df[~routes_df[col].isin(["\\N", "", None])]
            routes_df= routes_df.dropna(subset=[col])

        # clean numeric
        routes_df["stops"] = pd.to_numeric(routes_df["stops"], errors="coerce").fillna(0).astype(int)

        routes_df["codeshare"] = routes_df["codeshare"].fillna("").astype(str)
        routes_df["equipment"] = routes_df["equipment"].fillna("").astype(str)

        # reset index
        df = routes_df.reset_index(drop=True)

        print(df.head())
        print(f"[routes] {len(df)} rows after cleaning")

        return df

        
    def create_route_edges(self, df):
        query = """
        MATCH (a:Airport {iata: $src})
        MATCH (b:Airport {iata: $dst})
        MERGE (a)-[:FLIGHT {
            airline: $airline,
            stops: $stops,
            equipment: $equipment
        }]->(b)
        """

        for _, row in df.iterrows():
            self.driver.execute_query(
                query,
                src=row["src_iata"],
                dst=row["dst_iata"],
                airline=row["airline_iata"],
                stops=int(row["stops"]),
                equipment=row["equipment"]
            )

        print(f"[routes] {len(df)} relationships created")


############# ROUTE PROPERTIES #############

    def load_airlines(self):
        pass

    def create_airline_nodes(self):
        pass


    def clean_airlines(self):
        pass

    

    def create_constraints(self):
        self.driver.execute_query(
            "CREATE CONSTRAINT airport_iata IF NOT EXISTS "
            "FOR (a:Airport) REQUIRE a.iata IS UNIQUE"
        )
        print("[schema] Constraint on Airport.iata created (or already exists)")




