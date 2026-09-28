import pymongo

uri = "mongodb://server:6z5WVGWPgIT77bocuv70R7947Uf7NWZYO8lRxTs3ZBWfTU_f@6a7e34d2-8ae6-4e0e-b8f7-880bf2442b17.asia-south1.firestore.goog:443/default?loadBalanced=true&tls=true&authMechanism=SCRAM-SHA-256&retryWrites=false"

client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000)
db = client["default"]
print("Connected! Collections:", db.list_collection_names())

res = db.users.update_one(
    {"userId": "cb46871c-52c5-4277-8df0-db8abf98410c"},
    {
        "$addToSet": {"fcmTokens": "cw7QvLD6SGmvbilaTRdy4u:APA91bHCxEhoKu_WSAz3HP5KHTbC27LWZq1v7O5zpuZxqCKH1okWUgrnUeTSyaXVyHb-O9l4bGtRO6zg224QjckqCrsJTooWJRL1a2-NkkYCyDQUxWL3Y5Q"},
        "$set": {
            "userId": "cb46871c-52c5-4277-8df0-db8abf98410c",
            "devices.Nothing_A069": {
                "deviceName": "Nothing A069",
                "platform": "android"
            }
        }
    },
    upsert=True
)
print("Write result:", res.acknowledged, res.upserted_id or "matched")

doc = db.users.find_one({"userId": "cb46871c-52c5-4277-8df0-db8abf98410c"})
print("Fetched written doc from Firestore via MongoDB:", doc)
