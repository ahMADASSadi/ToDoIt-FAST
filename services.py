import importlib.util
from fastapi import Request

from motor.motor_asyncio import AsyncIOMotorCollection

from config.settings import MIGRATIONS_PATH


async def get_next_pk(collection: AsyncIOMotorCollection, counter_name: str) -> int:
    counter = await collection.database.counters.find_one_and_update(
        {"_id": counter_name},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    return counter["sequence_value"]


async def get_tasks_collection(request: Request) -> AsyncIOMotorCollection:
    return request.app.state.db["tasks"]


def convert_id(document: dict) -> dict:
    if document and "_id" in document:
        document["_id"] = str(document["_id"])
    return document


def run_migration(migration_file):
    # Construct full file path
    migration_path = MIGRATIONS_PATH/migration_file

    # Import the migration script dynamically
    spec = importlib.util.spec_from_file_location(
        migration_file, migration_path)
    
    migration_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration_module)

    # Assuming the migration function is named `migrate` in each file
    if hasattr(migration_module, "migrate"):
        migration_module.migrate()
    else:
        print(f"Migration function not found in {migration_file}")
