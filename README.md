
Inventory Expiry Tracker
Inventory Expiry Tracker is a Python + SQL Server concept project inspired by working as a console operator at an OTR convenience store. It replaces manual expiry checks with a simple system that logs deliveries and automatically flags products that are about to expire.
Problem
In a typical servo / convenience store, staff receive daily deliveries across grocery, dairy, and other perishable lines. Use‑by dates are tracked manually on paper or by walking the shelves, which is:
* Time‑consuming for staff at busy periods
* Error‑prone, especially with short‑dated products
* Likely to miss products that expire between checks
Solution Overview
This project designs a small inventory subsystem where:
* Each delivery docket line is recorded with product barcode, quantity, and use‑by date.
* All deliveries are stored in a SQL Server database with a normalised schema.
* A daily job queries the database and raises alerts for any delivery that expires within the next 24 hours.
* Staff can then remove or discount those products before they go out of date.
Although the database is designed for Microsoft SQL Server, the code is written to be portable and could be adapted to other relational databases.
Tech Stack
* Python 3 (virtual environment, pyodbc for database access)
* SQL Server (schema design and T‑SQL scripts)
* Windows Task Scheduler (for running the daily alert job in a production setup)
Database Design
The schema is normalised to 3NF and uses three main tables:
* ProductsStores one row per distinct product (barcode, name, category).
* DeliveriesStores each delivery batch of a product, including quantity, use‑by date, and received timestamp.
* AlertsStores expiry alerts raised against specific deliveries, including when the alert was generated and its status (e.g. Pending, Actioned).
The schema is defined in sql/001_init_schema.sql.
Python Components
* src/db.pyDatabase access layer. Contains:
    * get_connection() – opens a connection to the SQL Server database (via pyodbc).
    * insert_delivery(...) – “upserts” a product by barcode and inserts a corresponding delivery row.
* src/testdb.pySimple test script that calls insert_delivery(...) with sample data. Intended for quick manual testing while developing.
(Additional scripts like a barcode‑scan interface and the scheduled alert checker can be added on top of this core.)
How the Alert Flow Works (Design)
1. When a delivery arrives, staff scan the pick‑sheet or product barcode and enter quantity and use‑by date.
2. The application calls insert_delivery(...), which:
    * Ensures a matching Products row exists for that barcode.
    * Inserts a new row into Deliveries with quantity and use‑by date.
3. Once per day (for example, 6:00 AM), a scheduled Python script:
    * Queries Deliveries for rows where UseByDate is within the next 24 hours and no “Actioned” alert exists.
    * Inserts a row into Alerts for each match and outputs a list of products for staff to check on the shop floor.
4. Staff action the list (wastage / markdown) and can update alert status to “Actioned”.
This workflow turns expiry management from a manual “walk the store and hope you catch everything” process into a predictable daily task.
Setup Notes
* The schema script is written for Microsoft SQL Server and assumes a database named InventoryExpiryDB.
* The Python code uses pyodbc and an ODBC driver for SQL Server; connection details (server, database, credentials) are configured via environment variables.
* On macOS the project is developed using a Python virtual environment; a production deployment would typically run on a Windows machine with SQL Server installed.
Status
This is a work‑in‑progress portfolio project focused on:
* Clean schema design for expiry tracking
* A clear Python data‑access layer
* A realistic operational flow grounded in real convenience‑store processes
Future improvements could include a small web or CLI interface for staff, reporting on wastage trends, or integrating with an existing POS/inventory system.
