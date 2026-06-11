import json
from pymongo import MongoClient
from datetime import datetime, timezone

file_path = "Texas Commission on Environmental Quality - Notices Of Violation (NOV).json"

with open(file_path, "r", encoding="utf-8") as f:
    payload = json.load(f)

columns = payload["meta"]["view"]["columns"]
column_names = [col["fieldName"] for col in columns]
rows = payload["data"]

client = MongoClient("mongodb://localhost:27017/")
db = client["tceq_project"]
collection = db["raw_nov_json"]

collection.delete_many({})

ingested_at = datetime.now(timezone.utc).isoformat()

docs = []
for row in rows:
    record = dict(zip(column_names, row))
    docs.append({
        "source": "tceq_nov_local_json",
        "file_name": file_path,
        "ingested_at": ingested_at,
        "raw_record": record
    })

batch_size = 1000
for i in range(0, len(docs), batch_size):
    collection.insert_many(docs[i:i + batch_size])
    print(f"Inserted {min(i + batch_size, len(docs))} of {len(docs)} records")

print("Done.")
print("Total documents in MongoDB:", collection.count_documents({}))