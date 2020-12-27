import json
import time

from HiPaasNeo4j.neo4jMethods import *

from src.createEdi import CreateEdi
from src.oneClaim import ClaimGenerator



neoConn = {
    "URI" : "54.149.167.1:7687",
    "USERNAME" : "neo4j",
    "PASSWORD" : "crypt"
}

# Initialize Neo4j Driver
def initializeNeo4jDriver(uri, username, password):
    while True:
        try:
            return Neo4jMethods(uri, username, password)
        except Exception as e:
            print (e)
            time.sleep(10)          # Sleep for a while
            initializeNeo4jDriver(uri, username, password)
            #sys.exit()

neoDriver = initializeNeo4jDriver(neoConn['URI'], neoConn['USERNAME'], neoConn['PASSWORD'])

def createLoopNodes(queries):
    for query in queries:
        neoDriver.executeQuery(query)

def getFile(name):
    cypher = "MATCH path = (:Loop_ISA {filename : '%s'})-[*]->(a) \
        WITH collect(path) as paths \
        CALL apoc.convert.toTree(paths, true) yield value \
        RETURN value" % (name)

    return neoDriver.executeQuery(cypher).single()["value"]


start = time.perf_counter()
file_tree = getFile("small.837")
print ("Network call to get data: ", time.perf_counter() - start)


start = time.perf_counter()
edi_obj = CreateEdi()
edi = edi_obj.Loop_ISA(file_tree.get("has_loop_isa"))
with open("testFiles/big_temp.edi", "w") as w:
    w.write(edi)
print ("Operation to create edi", time.perf_counter() - start)



start = time.perf_counter()
clm_list__obj = ClaimGenerator()
claim_list = clm_list__obj.get_claim_list(file_tree.get("has_loop_isa"))
with open("testFiles/claim_list.json", "w") as w:
    json.dump(claim_list, w, indent = 4)
print (len(claim_list), "claims")
print ("Generate claim list", time.perf_counter() - start)