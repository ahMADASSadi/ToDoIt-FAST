# Simple ToDo app with FastAPI and MongoDB

This app is simply using 4 routes for `CRUD` operations
> [!NOTE]
> **Totaly written with the asynchronous compatibilities of FastAPI and Motor(For Async MongoDB connections)**
>
> To run: `python main.py` or `python main.py run`
>
> To apply the migrations listed in the `database/migrations` folder : `python main.py migrate`
***
> [!IMPORTANT]
> Migrations handling could be a bit challenging, since it must be written by user; based on the changes they applied to the database
>
> But,also note, since this is a MongoDB database you are not to necessarily have some migrations. of course other than you don't have a explicit `reponse_model`
