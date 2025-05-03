from contextlib import asynccontextmanager
from dotenv import load_dotenv
from typing import Optional
from pathlib import Path
import logging
import os


from pymongo.errors import ConfigurationError, CollectionInvalid
from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio import Redis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Base directory and environment configuration
BASE_DIR = Path(__file__).resolve().parent.parent
MIGRATIONS_PATH = BASE_DIR/"database"/"migrations"
load_dotenv(BASE_DIR / ".env")

# Database configuration from environment variables with defaults
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
DB_NAME = os.getenv("DB_NAME", "todoapp")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "tasks")

# Global variables for database clients
mongo_client: Optional[AsyncIOMotorClient] = None
db = None


@asynccontextmanager
async def lifespan(app):
    global mongo_client, db
    try:
        # Initialize MongoDB connection
        mongo_client = AsyncIOMotorClient(
            MONGO_URI,
            serverSelectionTimeoutMS=5000  # 5 second timeout
        )
        await mongo_client.server_info()  # Test connection
        logger.info("✅ Successfully connected to MongoDB")

        db = mongo_client[DB_NAME]
        app.state.db = db

        # Initialize Redis connection
        # redis_session = Redis(
        #     host=REDIS_HOST,
        #     port=REDIS_PORT,
        #     db=0,
        #     decode_responses=True,
        #     retry_on_timeout=True
        # )
        # await redis_session.ping()  # Test connection
        # logger.info("✅ Successfully connected to Redis")
        # app.state.redis = redis_session

        # Ensure collection and index
        try:
            collections = await db.list_collection_names()
            if COLLECTION_NAME not in collections:
                await db.create_collection(COLLECTION_NAME)
                logger.info(f"📁 Created collection: {COLLECTION_NAME}")
            else:
                logger.info(f"📂 Collection exists: {COLLECTION_NAME}")

            # Create index with error handling
            await db[COLLECTION_NAME].create_index("pk", unique=True)
            logger.info("📇 Created index 'pk' on collection")

        except CollectionInvalid as e:
            logger.error(f"Failed to create collection: {e}")
            raise

        yield

    except ConfigurationError as e:
        logger.error(f"Database connection failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during startup: {e}")
        raise
    finally:
        # Cleanup resources
        if mongo_client:
            mongo_client.close()
            logger.info("🛑 MongoDB connection closed")

        # if 'redis_session' in locals():
        #     await redis_session.aclose()
        #     logger.info("🛑 Redis connection closed")
