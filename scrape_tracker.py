import csv
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.bfmr.com/"
OUTPUT_FILE = "bfmr.csv"
API_KEY = os.getenv("BFMR_API_PUBLIC_KEY")
API_SECRET = os.getenv("BFMR_API_SECRET_KEY")

if not API_KEY or not API_SECRET:
    raise ValueError("Missing API keys. Please check your .env file.")

FIELDNAMES = [
    "Status", "Item", "QTY Purchased", "Order Number", "Tracking",
    "Payout Per Item", "Total Payout", "QTY Received", "Amount Paid",
    "Date Reserved", "Date Processed", "Date Paid"
]

HEADERS = {
    "API-KEY": API_KEY,
    "API-SECRET": API_SECRET
}

def get_tracker():
    url = f"{BASE_URL}api/v2/my-tracker"
    response = requests.get(url, headers=HEADERS)
    if (response.status_code == 200):
        return response.json()
    else:
        raise Exception(f"Failed to retrieve tracker data: {response.status_code}")

def main():
    try:
        all_reservations = []
        # Get raw tracker data
        tracker_data = get_tracker().get("my_tracker")

        for reservation in tracker_data:
            status = reservation.get("status")
            item_name = reservation.get("item_name")

            # Payout will only show if status is paid
            amount_paid = 0
            if (status == "paid"):
                amount_paid = reservation.get("total_payout")

            # Skip closed or insurance items
            if (status != "closed" and item_name != "BFMR Insurance"):
                row = {
                    "Status": status,
                    "Item": item_name,
                    "QTY Purchased": reservation.get("qty"),
                    "Order Number": reservation.get("order_id"),
                    "Tracking": reservation.get("tracking_number"),
                    "Payout Per Item": reservation.get("payout_price"),
                    "Total Payout": reservation.get("total_payout"),
                    "QTY Received": reservation.get("qty_received"),
                    "Amount Paid": amount_paid,
                    "Date Reserved": reservation.get("reserved_at"),
                    "Date Processed": reservation.get("date_processed"),
                    "Date Paid": reservation.get("date_paid")
                }
                all_reservations.append(row)
        
        all_reservations.sort(key=lambda x: (x["Date Reserved"], x["Item"]))

        # Write to a CSV file
        with open(OUTPUT_FILE, "w", newline='', encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(all_reservations)

    except Exception as e:
        print(f"Error. {e}")

if __name__ == "__main__":
    main()