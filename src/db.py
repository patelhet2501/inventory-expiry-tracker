"""Database access layer for the Inventory Expiry Tracker.

Connects to a local SQL Server instance using pyodbc and Windows
Authentication. Connection settings can be overridden via environment
variables so the module works on other machines without code changes.
"""

import os

import pyodbc

# Connection settings. Override via environment variables if your local
# setup differs (e.g. a different instance name or a remote server).
DB_DRIVER = os.getenv("INVENTORY_DB_DRIVER", "ODBC Driver 18 for SQL Server")
DB_SERVER = os.getenv("INVENTORY_DB_SERVER", r"localhost\SQLEXPRESS")
DB_NAME = os.getenv("INVENTORY_DB_NAME", "InventoryExpiryDB")


def get_connection():
    """Open and return a live pyodbc connection to InventoryExpiryDB.

    Uses Windows Authentication (Trusted_Connection=yes). The caller is
    responsible for closing the connection (or using it as a context
    manager).
    """
    connection_string = (
        "DRIVER={" + DB_DRIVER + "};"
        f"SERVER={DB_SERVER};"
        f"DATABASE={DB_NAME};"
        "Trusted_Connection=yes;"
    )
    return pyodbc.connect(connection_string)


def insert_delivery(barcode, name, category, quantity, use_by_date):
    """Record a delivery, upserting the parent product as needed.

    Ensures a Products row exists for ``barcode`` (inserting it if not),
    then inserts a Deliveries row referencing that product. Both writes
    happen inside a single transaction, so either everything commits or
    nothing does.

    Args:
        barcode: Product barcode (unique key used for the upsert).
        name: Product display name (used when inserting a new product).
        category: Product category (used when inserting a new product).
        quantity: Number of units received in this delivery.
        use_by_date: Use-by date for this delivery (``datetime.date`` or
            an ISO ``YYYY-MM-DD`` string).

    Returns:
        The DeliveryID of the newly inserted delivery row.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Upsert the product: insert only if the barcode is not present.
        cursor.execute(
            """
            IF NOT EXISTS (SELECT 1 FROM dbo.Products WHERE Barcode = ?)
                INSERT INTO dbo.Products (Barcode, Name, Category)
                VALUES (?, ?, ?);
            """,
            barcode, barcode, name, category,
        )

        # Resolve the ProductID for this barcode.
        cursor.execute(
            "SELECT ProductID FROM dbo.Products WHERE Barcode = ?;",
            barcode,
        )
        product_id = cursor.fetchone()[0]

        # Insert the delivery and capture its generated DeliveryID.
        cursor.execute(
            """
            INSERT INTO dbo.Deliveries (ProductID, Quantity, UseByDate)
            OUTPUT INSERTED.DeliveryID
            VALUES (?, ?, ?);
            """,
            product_id, quantity, use_by_date,
        )
        delivery_id = cursor.fetchone()[0]

        conn.commit()
        return delivery_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
