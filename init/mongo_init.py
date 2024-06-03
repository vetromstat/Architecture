from pymongo import MongoClient
from pydantic import BaseModel
from datetime import datetime
from bson import ObjectId


class Delivery(BaseModel):
    sender_id: int
    receiver_id: int
    status: str
    date: datetime = datetime.now().date()


class Parcel(BaseModel):
    sender_id: int
    receiver_id: int
    delivery_id: str
    status: str
    shipment_method: str


if __name__ == "__main__":

    client = MongoClient(f"mongodb://mongo:mongo@mongo:27017/")
    db = client.get_database("arch")
    deliveries_collection = db.get_collection("deliveries_collection")
    parcels_collection = db.get_collection("parcels_collection")

    if deliveries_collection.count_documents({}) > 0:
        deliveries_collection.delete_many({})
    if parcels_collection.count_documents({}) > 0:
        parcels_collection.delete_many({})

    def create_parcel(delivery_id: str, tracking_id: int, status: str, shipment_method: str) -> Parcel:
        delivery = deliveries_collection.find_one(
            {"_id": ObjectId(delivery_id)})
        if delivery:
            parcel = Parcel(
                sender_id=delivery["sender_id"],
                receiver_id=delivery["receiver_id"],
                tracking_id=tracking_id,
                delivery_id=delivery_id,
                status=status,
                shipment_method=shipment_method
            )
            parcels_collection.insert_one(parcel.dict())
            return parcel
        else:
            raise ValueError("Delivery not found")

    def init_mongo():
        db_result = deliveries_collection.insert_one(Delivery(
            sender_id=1, receiver_id=2, status="pending", date=datetime.now().date()).dict())
        inserted_id = db_result.inserted_id
        parcel = create_parcel(str(inserted_id), 123456, "in_transit", "plane")
        print(
            f"MongoDB succesfully initialized with data {list(deliveries_collection.find())} and {list(parcels_collection.find())}")

    init_mongo()
