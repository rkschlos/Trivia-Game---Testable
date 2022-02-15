# Trivia Game

This is a full implementation of the React-based trivia game
with API implementations in MongoDB and PostgreSQL. This
README.md file contains information about how it all works,
as well as how it was created.

## The process of creating an application from scratch

This application is an **example** application, but has
portions to it that would be applicable to building a
microservice-based application with a unified React
front-end.

## Using .gitignore

Create a _.gitignore_ file in the root of your application.
Copy the contents of the
<https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore>
into the _.gitignore_ file in your application. This will
prevent files from a Python application that should not be
committed to your does not get committed.

## Windows and macOS

To make sure that Windows and macOS properly use your
application, it's important that the files get created by
Git properly. To make sure this happens, copy the
_.gitattributes_ file from the root directory of the project
to the root directory of your project.

Inside there, it tells Git to make sure that all files that
end with `.sh` are handled in a special way so that the
containers running in your application can properly read
them.

## Creating the front-end

Because of differences in the way that Docker on Windows and
Docker on not-Windows works, we set up the React front-end
so that both operating systems can work on the same
codebase.

To create the React application, we use the
`create-react-app` tool. To do that, we start a container
running the newest stable version of Node.js called "Node
LTS". (LTS means "long-term support".) It's important that
the version of Node that we use to create the React
application is the **same** version used in the
_docker-compose.yml_ file.

```sh
docker run -it -v "$(pwd):/app" -w "/app" node:lts-bullseye bash
```

This starts an active container running Node LTS. You can
then use the `create-react-app` utility to initialize your
React application.

```sh
npx create-react-app ghi
```

Once that is built, to support folx using Windows, copy the
two files in _resources/ghi_ into the _ghi_ directory. Then,
change the `scripts.start` entry in the _ghi/package.json_
file to read like this.

```json
"start": "node ./windows-setup.js && react-scripts start",
```

That will run the _windows-setup.js_ file before starting
the React application. This runs for **everyone** and will
apply the changes needed **only if** the person running it
is on Windows. This way, you can have a single common
codebase for any developer on the team.

In your _docker-compose.yml_ file, add this section for the
front-end service of your application.

```yaml
ghi:
  image: node:lts-bullseye
  command: /bin/bash run.sh
  working_dir: /app
  volumes:
    - ./ghi:/app
  ports:
    - "3000:3000"
  environment:
    HOST_OS: ${OS}
    NODE_ENV: development
    HOST: "0.0.0.0"
    REACT_APP_API_HOST: http://localhost:8000
```

* The `HOST_OS` and `NODE_ENV` environment variables are
  used for the _windows-setup.js_ script.
* The `HOST` environment variable is used to start the React
  development server in a way that you can connect to it
  from outside the Docker container.
* The `REACT_APP_API_HOST` is used by the React application
  to specify the host that the front-end will connect to
  when making `fetch` calls to the API

### Troubleshooting

The most common problem that occurs is that the app doesn't
start because of a bad installation of packages in the
`node_modules` directory. This is like having a bad
installation of Python packages in your virtual environment.

This can occur for a number of reasons. The easiest way to
fix this is to stop your services, delete the `node_modules`
directory in the _ghi_ directory, then start your services,
again. While it's starting, just sit back and let it do its
thing. Then, once the React development server is running,
again, give it a go.

## Creating a FastAPI backend

To create a FastAPI backend, you'll want three files:

* A _requirements.txt_ file that contains the packages you
  want to install
* A _Dockerfile.dev_ file that contains the commands to
  build the image
* A Python file for **uvicorn** to run when it starts

In this sample application, you can find each of those files
in the _api_ directory.

Normally, a single microservice will **not** use more than
one database. The **api** application is different because
it is meant to demonstrate access to PostgreSQL and MongDB.
Unless your microservice must connect to two different kinds
of data stores, don't have different API calls based on
those.

However, the database access pattern **is** suggested for
you to use. Check out the _db.py_ file in both the MongoDB
and PostgreSQL directories to see how they work.

## Creating a PostgreSQL database

Using a relational database in your application is
straight-forward. You just need to know the details about
how the PostgreSQL RDBMS will run when it **first** starts
up. That's the important part, when it **first** starts up.

It's at times like these where reading the documentation for
the [PostgreSQL image](https://hub.docker.com/_/postgres) is
very important. Here are the environment variables that are
important, according to the documentation. They are **only**
used when the PostgreSQL RDBMS runs **the first time**.

| Variable          | Purpose                                               |
|-------------------|-------------------------------------------------------|
| POSTGRES_PASSWORD | **REQUIRED**: Sets the password for the database user |
| POSTGRES_USER     | Sets the name of the database user                    |
| POSTGRES_DB       | Sets the name of the database                         |

If you want the RDBMS to import data or run SQL when it
starts up the first time, like create your tables or other
databases, then you must create one or more `.sql` files and
configure the volumes for PostgreSQL to find them. To do
that, you must set the volume on your local drive to point
to the directory that contains the initialization scripts.
If you change the tables or add new tables, you'll need to
stop your services, prune your containers, remove the volume
that contains your database data, create the volume, again,
then bring your services back up.

The initialization will read your SQL files in alphabetical
order. It helps to name them with numbers at the beginning
of each file so that they will be read in the correct order
by the initialization script.

You can see in the _data/postgres/init_ directory three
files that will be used to initialize the database. The
first creates the database and the user for the trivia game.
The second creates the tables. The third imports data.

The second and third scripts start with the line that
connects the script to the database where you want to create
the tables in. Make sure you do that in your scripts.

There is something important to note, here. At the end of
the table creation script, you **must** alter the owner of
the table to the user that you created in the first script.
Otherwise, the database user created in the first script
will not have permission to interact with the table.

You can use this entry in _docker-compose.yml_ for it to run
the initialization scripts for you if you follow the same
directory layout. Remember, if you add or change them, you
will need to remove and recreate the volume as described
above.

Make sure you **change the name of the volume** to something
that makes sense for your application.

```yaml
postgres:
  image: postgres:14-bullseye
  volumes:
    # For your initialization scripts
    - ./data/postgres/init:/docker-entrypoint-initdb.d
    # For the data stored by PostgreSQL
    - relational-trivia:/var/lib/postgresql/data
  environment:
    # Password for the postgres superuser
    # See 01-create-databases.sql for the name/password
    #   for the user of the application database
    POSTGRES_PASSWORD: secret
```

If you want to use pgAdmin during your development, you can
add this to your _docker-compose.yml_ file, too. Make sure
you **change the name of the volume** to something that
makes sense for your application. Also, change the email and
password for the default login, if you want.

```yaml
pgadmin:
  image: dpage/pgadmin4
  volumes:
    - pgadmin-trivia:/var/lib/pgadmin
  ports:
    - 8082:80
  environment:
    PGADMIN_DEFAULT_EMAIL: person@example.com
    PGADMIN_DEFAULT_PASSWORD: password
    PGADMIN_DISABLE_POSTFIX: 1
```

### Troubleshooting

The SQL scripts are likely to be the cause of your database
not being properly created. Watch the log files for your
database instance. If you see an error message about one of
the `.sql` files, you'll need to stop your services, remove
and recreate the volume for the relational database, then
bring your services back up.

## Creating a MongoDB database

Using MongoDB in your application is straight-forward. You
just need to know the details about how the MongoDB DDBMS
will run when it **first** starts up. That's the important
part, when it **first** starts up.

It's at times like these where reading the documentation for
the [MongoDB image](https://hub.docker.com/_/mongo) is very
important. Here are the environment variables that are
important, according to the documentation. They are **only**
used when the MongoDB DDBMS runs **the first time**. Note
that none of them are required.

| Variable                   | Purpose                                 |
|----------------------------|-----------------------------------------|
| MONGO_INITDB_ROOT_PASSWORD | Sets the password for the database user |
| MONGO_INITDB_ROOT_USERNAME | Sets the name of the database user      |
| MONGO_INITDB_DATABASE      | Sets the name of the database           |

If you want the DDBMS to import data or run JavaScript when
it starts up the first time, like create your database or
other databases, then you must create one or more `.js`
files and configure the volumes for MongoDB to find them. To
do that, you must set the volume on your local drive to
point to the directory that contains the initialization
scripts. If you change the tables or add new tables, you'll
need to stop your services, prune your containers, remove
the volume that contains your database data, create the
volume, again, then bring your services back up.

The initialization will read your JavaScript files in
alphabetical order. It helps to name them with numbers at
the beginning of each file so that they will be read in the
correct order by the initialization script.

You can see in the _data/mongo/init_ directory four files
that will be used to initialize the database. The first
creates the user for the trivia game. The second creates the
collections. The third imports data. The fourth creates
indexes.

All three scripts start with the line that connects the
script to the database where you want to create the user,
collections, and documents in. Make sure you do that in your
scripts.

You can use this entry in _docker-compose.yml_ for it to run
the initialization scripts for you if you follow the same
directory layout. Remember, if you add or change them, you
will need to remove and recreate the volume as described
above.

Make sure you **change the name of the volume** to something
that makes sense for your application.

```yaml
mongo:
  image: mongo:5
  volumes:
    # For your initialization scripts
    - ./data/mongo/init:/docker-entrypoint-initdb.d
    # For the data stored by MongoDB
    - document-trivia:/data/db
  environment:
    # Set for use by Mongo Express
    MONGO_INITDB_ROOT_USERNAME: root
    MONGO_INITDB_ROOT_PASSWORD: password
```

If you want to use Mongo Explress during your development,
you can add this to your _docker-compose.yml_ file, too.
Make sure you **change the name of the environment variables
to match what is in your create scripts**.

```yaml
mongo-express:
  image: mongo-express:latest
  depends_on:
    - mongo
  ports:
    - "8081:8081"
  environment:
    # Authentication information from above
    ME_CONFIG_MONGODB_ADMINUSERNAME: root
    ME_CONFIG_MONGODB_ADMINPASSWORD: password
    # URL to MongoDB installation
    ME_CONFIG_MONGODB_URL: mongodb://root:password@mongo:27017/
```

### Troubleshooting

Sometimes, Mongo Express starts "too early". If that happens
and you see it "Exited" in the list of Docker containers in
the Docker Dashboard, just start it by clicking the Play
button after MongoDB comes up.

The JavaScript initialization scripts are likely to be the
cause of your database not being properly created. Watch the
log files for your database instance. If you see an error
message about one of the `.js` files, you'll need to stop
your services, remove and recreate the volume for the
relational database, then bring your services back up.

The other thing is if you're creating `ObjectId` values for
links between documents. In the scripts, those **must** be
24-character strings of the number 0-9 and letters A-F.
Nothing else will work.
