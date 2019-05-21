from mongoengine import Document, PointField, IntField


class MongoGarbagePoint(Document):
    garbage_ptr = IntField()
    point = PointField(auto_index=True)
