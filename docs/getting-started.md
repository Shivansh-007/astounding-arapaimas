# Getting Started Guide

## Running The Game

You can run the frontend through poetry in the following way:
```bash
# Active the poetry environment
poetry shell
# Run the `app` module
python -m app
```
or you can do both the steps in one command as `poetry run python -m app`

The game requires two players to be run and played successfully and you will 
probably not be hosting this API on a server, so you can open two instances of 
this game once you start the API and configure the env variables like show here. 
Once the two are running you would now be asked for the password, now the 
problem comes that you won't be able to enter the two tokens after entering them
once for each, this happens because:

https://github.com/p0lygun/astounding-arapaimas/blob/main/app/game_manager.py#L231..L237

```py
if os.path.exists(cache_path):
    # Read file token from file as cache exists
    with open(cache_path, "r", encoding="utf-8") as file:
        token = (json.load(file)).get("token")
        if token:
            return token
```
This takes the token from the cache file if it is found, when it is not found
it would take it from input and then store it in the cache file if the token
is valid (it validates it through the API you have linked in `.env`). Once you 
have entered the token it would be stored their and would be used always you cannot
enter two separate tokens. To overcome this problem you can comment out these
lines and make the TUI app ask you the token everytime.
