from fastapi import FastAPI

from routers.todo import router as todo_router
from config.settings import lifespan

app = FastAPI(debug=False, lifespan=lifespan)
app.include_router(todo_router, prefix="/tasks")

if __name__ == "__main__":
    from uvicorn import run

    if len(sys.argv) > 1:
        arguments = sys.argv[1:]
        for arg in arguments:
            match arg:
                case "run":
                    run("main:app", host="127.0.0.1", port=8000, reload=True)
                case "migrate":
                    import sys
                    import os

                    from services import MIGRATIONS_PATH, run_migration

                    migrations = os.listdir(MIGRATIONS_PATH)
                    print(f"Found migrations: {migrations}")

                    python_migrations = [
                        migration for migration in migrations if migration.endswith(".py")]
                    print(f"Running migrations: {python_migrations}")
                    tasks = [run_migration(migration)
                             for migration in python_migrations]
                case _:
                    print("No Valid argument passed!")
    else:
        # Default behavior if no argument is provided
        run("main:app", host="127.0.0.1", port=8000, reload=True)
