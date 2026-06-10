
from db import insert_delivery

if __name__ == "__main__":
    delivery_id = insert_delivery(
        barcode="1234567890123",
        name="Test Milk 2L",
        category="Dairy",
        quantity=10,
        use_by_date="2026-06-20",
    )
    print("Inserted delivery:", delivery_id)