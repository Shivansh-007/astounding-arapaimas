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

### **3. Run The API**
The project can be started by running it directly on your system.The environment variables shown in a previous section need to have been configured.

- **Database**

    First, start the PostgreSQL database.
    Note that this can still be done with Docker even if the webserver will be running on the host - simply adjust the `DATABASE_URL` environment variable accordingly.

- **Webserver**

    Starting the webserver is done simply through poetry:

    ```shell
    poetry run task start
    ```
