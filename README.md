# API for Payments, Customer, and Banks

The project implements a FastAPI API that allows the user to interact with a SQL database (PostgreSQL in this case) to generate payment records and customer records.

## Installation

Clone the repository.

```bash
git clone https://github.com/JoseJimArg/crediclub-challenge.git
cd crediclub-challenge/
```

Once inside, it is recommended to use a virtual environment. I recommend using `pyenv` with a `python >= 3.10.x` version.

### Install dependencies
Requires `pip` to be installed.

```bash
pip install -r requirements.txt
```

### .env File
The `.env` file must be created in the root of the project for it to be read. Only the database URL needs to be configured.

### Configure the database
The `database/database.py` file contains the configured URL for the database. The URL should be taken from the `.env` file using the variable name `DATABASE_URL`.

You can use any SQL-compatible database of your choice as long as it is compatible with `sqlalchemy`. Visit https://docs.sqlalchemy.org/en/20/ for more information.

## Usage

To run the project, the first step is to perform the migration to the database. You must have the database installed and the URL configured beforehand in the `.env` file.

To execute all commands, you need to be in the project's root directory.

### Perform database migration

```bash
python migrate_db.py
```

### Import data from xlsx files
```bash
python import_data_xlsx.py
```

### Run the API with uvicorn
```bash
uvicorn main:app --reload
```

The `--reload` option will automatically reload the server when code changes are made, eliminating the need to manually restart the local server.

## Try on live!
Comming soon... (?