# Setup

## API Setup

### **1. PostgreSQL setup**

Enter psql, a terminal-based front-end to PostgreSQL:

```shell
psql -qd postgres
```

Run the following queries to create the user and database:

```sql
CREATE USER arapaimas WITH SUPERUSER PASSWORD 'arapaimas';
CREATE DATABASE arapaimas WITH OWNER arapaimas;
```

Finally, enter `/q` to exit psql.

### **2. Environment variables**

The API is configured through the following environment variables:

- **`DATABASE_URL`**: A string specifying the PostgreSQL database to connect to,
  in the form `postgresql://user:password@host/database`, such as
  `postgresql://arapaimas:arapaimas@localhost:7777/arapaimas`

- **`CLIENT_ID`**: Discord app client ID
    > To setup your discord application go to discord.com/developers/applications and create a new application.

- **`CLIENT_SECRET`**: Discord app client secret

- **`AUTH_URL`**: Under OAuth2 add the redirect `{BASE_URL}/callback`, we only need the identify scope. Use the generatred URL for the `AUTH_URL` env var.

- **`LOG_LEVEL`**: Any valid Python `logging` module log level - one of `DEBUG`,
  `INFO`, `WARN`, `ERROR` or `CRITICAL`. When using debug mode, this defaults to
  `INFO`. When testing, defaults to `ERROR`. Otherwise, defaults to `WARN`.

- **`JWT_SECRET`**: A 32 byte (64 digit hex string) secret for encoding tokens. Any value can be used.

- **`API_URL`**: The URL hosting the API, if you are running with docker or poetry, it is most likely to `http://127.0.0.1:8000`

- **`WEBSOCKET_URL`**: The URL hosting the API but with websocket schema, which is most likely to be `ws://127.0.0.1:8000`, in-case you are using external services which have `https` enabled then make sure to use `wss` in the URL.

 - **Example `.env`**
    ```env
    CLIENT_ID="863943137139621908"
    CLIENT_SECRET="TheUltimateClientSecretMadeByDiscord"
    JWT_SECRET="c78f1d852e2d5adefc2bc54ed256c5b0c031df81aef21a1ae1720e7f72c2d39"

    AUTH_URL="https://discord.com/api/oauth2/authorize?client_id=863943137139621908&redirect_uri=http%3A%2F%2F127.0.0.1%3A8000%2Fcallback&response_type=code&scope=identify"

    LOG_LEVEL="debug"

    DATABASE_URL="postgresql://arapaimas:arapaimas@localhost:7777/arapaimas"
    API_URL="http://127.0.0.1:8000"
    WEBSOCKET_URL="ws://127.0.0.1:8000"
    ```

### **3. Run The API**
The project can be started by running it directly on your system.The environment variables shown in a previous section need to have been configured.

- **Database**

    First, start the PostgreSQL database.
    Note that this can still be done with Docker even if the webserver will be running on the host - simply adjust the `DATABASE_URL` environment variable accordingly.

- **Migrations**

    Once the Database is started, you need run migrations to init tables and columns which can be ran through `alembic upgrade heads`, but I would say it would be better to run `poetry run bash scripts/prestart.sh`

- **Webserver**

    Starting the webserver is done simply through poetry:

    ```shell
    poetry run task start
    ```
