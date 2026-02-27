
# Healthcare Agent Tools
import json
from neo4j import GraphDatabase

# Connection will be initialized in Part 4
conn = None

def init_connection(uri, user, password):
    global conn
    class Neo4jConn:
        def __init__(self, uri, user, password):
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
        def run_query(self, query, parameters=None):
            with self.driver.session() as session:
                result = session.run(query, parameters or {})
                return [record.data() for record in result]
    conn = Neo4jConn(uri, user, password)
    return conn

# Bed Management Tools
def get_available_beds(department: str = None) -> str:
    if department:
        query = "MATCH (d:Department {name: $dept})-[:HAS_BED]->(b:Bed {status: 'available'}) RETURN d.name as department, count(b) as available_beds"
        result = conn.run_query(query, {"dept": department})
    else:
        query = "MATCH (d:Department)-[:HAS_BED]->(b:Bed {status: 'available'}) RETURN d.name as department, count(b) as available_beds ORDER BY d.name"
        result = conn.run_query(query)
    return json.dumps(result, indent=2)

def get_icu_status() -> str:
    query = "MATCH (d:Department {name: 'ICU'})-[:HAS_BED]->(b:Bed) RETURN b.status as status, count(b) as count ORDER BY b.status"
    return json.dumps(conn.run_query(query), indent=2)

def get_discharge_candidates() -> str:
    query = "MATCH (p:Patient)-[:ADMITTED_TO]->(b:Bed)<-[:HAS_BED]-(d:Department) WHERE p.status IN ['ready_for_discharge', 'recovering'] RETURN p.name as patient, p.status as status, p.condition as condition, d.name as department ORDER BY p.status DESC"
    return json.dumps(conn.run_query(query), indent=2)

def get_low_stock_items() -> str:
    query = "MATCH (d:Department)-[:STOCKS]->(i:InventoryItem) WHERE i.quantity < i.minStock RETURN i.name as item, i.type as type, i.quantity as current_qty, i.minStock as min_required, d.name as department ORDER BY (i.minStock - i.quantity) DESC"
    return json.dumps(conn.run_query(query), indent=2)

def get_physicians_on_call() -> str:
    query = "MATCH (p:Physician {onCall: true})-[:ASSIGNED_TO]->(d:Department) RETURN p.name as physician, p.specialty as specialty, d.name as department"
    return json.dumps(conn.run_query(query), indent=2)

def execute_cypher_query(query: str) -> str:
    try:
        return json.dumps(conn.run_query(query), indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})
