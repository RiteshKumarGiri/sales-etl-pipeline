# Sales ETL Pipeline

A Python-based ETL (Extract, Transform, Load) pipeline that cleans messy retail sales data and loads it into a PostgreSQL database for analysis. Built as a hands-on project to apply data engineering fundamentals: data cleaning, transformation, incremental database loading, SQL analysis, and production-style logging/error handling.

## What It Does

1. **Extract** – Reads raw sales data from a CSV file (path configurable via CLI)
2. **Transform** – Cleans and standardizes the data:
   - Removes fully blank and duplicate rows
   - Fills missing customer names with `"Unknown"`
   - Drops rows with missing price or quantity
   - Filters out invalid orders (zero or negative quantity)
   - Parses inconsistent date formats (`YYYY-MM-DD`, `DD/MM/YYYY`, `DD-MM-YYYY`, `MM/DD/YYYY`) into a single standardized date type
   - Adds derived columns: `total_price` and `order_month`
3. **Load** – Performs **incremental loading** into PostgreSQL:
   - Checks which `order_id`s already exist in the target table
   - Inserts only new rows, skipping ones already loaded
   - Avoids the need to fully wipe and reload the table on every run
4. **Analyze** – SQL queries for business insights:
   - Total revenue
   - Top 5 customers by spend
   - Average order value per product
   - Highest-revenue month

The pipeline is configurable from the command line, logs each stage's progress and row counts, and fails gracefully with a clear error message instead of a raw traceback if something goes wrong.

## Tech Stack

- **Python** – pandas for data cleaning/transformation
- **PostgreSQL** – data storage
- **SQLAlchemy + psycopg** – database connectivity
- **python-dotenv** – secure credential management
- **argparse** – configurable CLI options
- **logging** – pipeline observability

## Project Structure

```
sales-etl-pipeline/
├── main.py            # ETL pipeline (extract, transform, load)
├── sales_data.csv     # Sample raw sales data (intentionally messy)
├── .env                # Database credentials (not committed — see setup)
├── .gitignore
└── README.md
```

## Setup & Usage

**1. Clone the repo**
```bash
git clone https://github.com/RiteshKumarGiri/sales-etl-pipeline.git
cd sales-etl-pipeline
```

**2. Install dependencies**
```bash
pip install pandas sqlalchemy psycopg2-binary python-dotenv
```

**3. Create a `.env` file** in the project root with your PostgreSQL credentials:
```
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sales_db
```

**4. Create the target database** in PostgreSQL (e.g., via pgAdmin):
```sql
CREATE DATABASE sales_db;
```

**5. Run the pipeline**

With defaults (reads `sales_data.csv`, loads into the `sales` table):
```bash
python main.py
```

With custom file/table names:
```bash
python main.py --file sales_data.csv --table sales
```

Running the pipeline multiple times is safe — it only inserts rows with `order_id`s not already present in the target table, so repeated runs don't create duplicates.

## Data Cleaning & Engineering Challenges Solved

This project intentionally uses messy, realistic sample data to practice common real-world data engineering problems:

- **Mixed date formats in one column** – solved with a custom parser that tries multiple known formats per row, rather than assuming a single format (which silently drops valid data via `errors='coerce'`).
- **Type mismatches between pandas and SQL** – e.g., pandas' `Period` type isn't understood by PostgreSQL and must be cast to a string before loading.
- **Secure credential handling** – database credentials are stored in a `.env` file (excluded from version control) rather than hardcoded, with special characters in passwords URL-encoded for use in connection strings.
- **Incremental loading** – instead of replacing the whole table on every run (which is slow and destroys any downstream changes), the pipeline checks existing primary keys and inserts only new records.
- **Graceful failure** – each pipeline stage is wrapped in logging and error handling, so failures produce a clear, timestamped message instead of a raw Python traceback.

## Sample Insights

| Metric | Result |
|---|---|
| Total Revenue | ₹525,713.71 |
| Top Product by Revenue | Wireless Mouse |
| Highest Revenue Month | January |

## Possible Next Steps

- Orchestration with Apache Airflow for scheduled, automated runs
- Migrate source data ingestion from static CSV to a live API
- Add data validation checks (e.g., schema checks, expected value ranges) before loading

## Author

Built by Ritesh Kumar Giri as a hands-on project while transitioning from Oracle PL/SQL development into Data Engineering.
