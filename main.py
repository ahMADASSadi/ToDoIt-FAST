from fastapi import FastAPI

from routers.todo import router as todo_router
from config.settings import lifespan

from services import migrate

app = FastAPI(debug=False, lifespan=lifespan)
app.include_router(todo_router, prefix="/tasks")

if __name__ == "__main__":
    from uvicorn import run
    import sys

    if len(sys.argv) > 1:
        arguments = sys.argv[1:]
        for arg in arguments:
            match arg:
                case "run":
                    run("main:app", host="127.0.0.1", port=8000, reload=True)
                case "migrate":
                    migrate()
                case _:
                    print("No Valid argument passed!")
    else:
        # Default behavior if no argument is provided
        run("main:app", host="127.0.0.1", port=8000, reload=True)
