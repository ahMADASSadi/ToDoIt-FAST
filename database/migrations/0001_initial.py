from motor.motor_asyncio import AsyncIOMotorClient


def migrate():
    from schemas.todo import TaskPriority
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["todoapp"]
    tasks = db["tasks"]

    # Update tasks missing 'priority' by setting it to 'medium'
    result = tasks.update_many(
        {"priority": {"$exists": False}},
        {"$set": {"priority": TaskPriority.medium}}
    )
    print(f"Migration took effect.")
