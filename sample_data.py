import pandas as pd
import json
import os

# Creates fake sales data to simulate a real database table
def create_sample_data():
    data = {
        "order_id": [1, 2, 3, 4, 5, 6, 7, 8, None],  # None = missing value (bad!)
        "customer_name": ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Heidi", "Ivan"],
        "amount": [100, 200, -50, 400, 500, 600, 700, 800, 900],  # -50 = negative (bad!)
        "status": ["completed", "completed", "pending", "completed", "INVALID", "completed", "pending", "completed", "completed"],  # INVALID = bad!
        "order_date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04",
                       "2024-01-05", "2024-01-06", "2024-01-07", "2024-01-08", "2024-01-09"]
    }

    df = pd.DataFrame(data)
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/orders.csv", index=False)
    print("✅ Sample data created at data/orders.csv")
    return df

# Creates a fake dbt manifest (normally dbt generates this automatically)
def create_mock_manifest():
    manifest = {
        "nodes": {
            "model.my_project.orders": {
                "name": "orders",
                "resource_type": "model",
                "columns": {
                    "order_id": {"name": "order_id", "data_type": "integer"},
                    "customer_name": {"name": "customer_name", "data_type": "varchar"},
                    "amount": {"name": "amount", "data_type": "float"},
                    "status": {"name": "status", "data_type": "varchar"},
                    "order_date": {"name": "order_date", "data_type": "date"}
                }
            }
        }
    }

    os.makedirs("target", exist_ok=True)
    with open("target/manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    print("✅ Mock manifest created at target/manifest.json")

# Creates fake dbt test results (normally dbt generates this after running tests)
def create_mock_run_results():
    run_results = {
        "results": [
            {
                "unique_id": "test.my_project.not_null_orders_order_id",
                "status": "fail",
                "failures": 1,
                "message": "Got 1 result, configured to fail if != 0",
                "execution_time": 0.5
            },
            {
                "unique_id": "test.my_project.accepted_values_orders_status",
                "status": "fail",
                "failures": 1,
                "message": "Got 1 result, configured to fail if != 0",
                "execution_time": 0.3
            },
            {
                "unique_id": "test.my_project.positive_amount_orders",
                "status": "fail",
                "failures": 1,
                "message": "Got 1 result, configured to fail if != 0",
                "execution_time": 0.4
            }
        ]
    }

    with open("target/run_results.json", "w") as f:
        json.dump(run_results, f, indent=2)
    print("✅ Mock run results created at target/run_results.json")

if __name__ == "__main__":
    create_sample_data()
    create_mock_manifest()
    create_mock_run_results()
    print("\n✅ All sample data ready! Now run: python monitor.py")