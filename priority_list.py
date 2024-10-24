from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
import csv

load_dotenv()
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
REPORTS_DIR = f"reports_{TIMESTAMP}"


def connect_to_mongodb():
    """Connects to mongo"""
    try:
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client[os.getenv("DB_NAME")]
        return db
    except Exception as e:
        print(f"Error occurred when connecting to database: \n{e}")
        return None


def get_all_sponsor_events():
    """
    Gets a list of all sponsor events in the database.
    Filters for only events that match email pattern (contains @).
    Returns a list of sponsor emails.
    """
    db = connect_to_mongodb()
    if db is None:
        return None

    try:
        users = db["users"]

        query = [
            # Get the event object keys (sponsor emails)
            {"$project": {"event_keys": {"$objectToArray": "$day_of.event"}}},
            {"$unwind": "$event_keys"},
            # Only keep keys that contain @ (email pattern)
            {"$match": {"event_keys.k": {"$regex": ".*@.*"}}},
            # Get unique sponsor emails
            {"$group": {"_id": "$event_keys.k"}},
            # Sort them alphabetically
            {"$sort": {"_id": 1}},
        ]

        sponsor_emails = [doc["_id"] for doc in users.aggregate(query)]

        print(f"\nFound {len(sponsor_emails)} sponsor emails:")
        for email in sponsor_emails:
            print(f"- {email}")

        return sponsor_emails

    except Exception as e:
        print(f"Error getting sponsor events: {e}")
        return None


def get_sponsor_list(sponsor_email: str):
    """
    Gets the list of users scanned by sponsors
    Returns two lists: A (regular) and B (special)
    """
    db = connect_to_mongodb()
    if db is None:
        return None, None

    try:
        users = db["users"]

        # Finds Users on the A list for a sponsor
        list_a_users = list(
            users.find(
                {f"day_of.event.{sponsor_email}.orgSponsorA": {"$exists": True}},
                {
                    "email": 1,
                    "first_name": 1,
                    "last_name": 1,
                    "_id": 0,
                },
            )
        )

        # Finds Users on the B list for a sponsor
        list_b_users = list(
            users.find(
                {f"day_of.event.{sponsor_email}.orgSponsorB": {"$exists": True}},
                {
                    "email": 1,
                    "first_name": 1,
                    "last_name": 1,
                    "_id": 0,
                },
            )
        )

        print(f"\nResults for sponsor {sponsor_email}:")
        print(f"Found {len(list_a_users)} users in priority list A")
        print(f"Found {len(list_b_users)} users in priority list B")

        return list_a_users, list_b_users

    except Exception as e:
        print(f"Error in get_sponsor_list: {e}")
        return None, None


def generate_report(sponsor_email: str):
    """
    Generates two CSV files (list A and list B) for a sponsor containing user details.
    """
    list_a, list_b = get_sponsor_list(sponsor_email)
    sponsor_name = sponsor_email.split("@")[0]
    
    # Generate List A CSV
    if list_a:
        file_name_a = f"{REPORTS_DIR}/{sponsor_name}_list_A.csv"
        with open(file_name_a, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["First Name", "Last Name", "Email"]) # Head
            for user in list_a:
                writer.writerow([
                    user.get("first_name", ""),
                    user.get("last_name", ""),
                    user.get("email","")
                ])
        print(f"List A saved to: {file_name_a}")

    # Generate List B CSV
    if list_b:
        file_name_b = f"{REPORTS_DIR}/{sponsor_name}_list_B.csv"
        with open(file_name_b, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["First Name", "Last Name", "Email"])  # Head
            for user in list_b:
                writer.writerow(
                    [
                        user.get("first_name", ""),
                        user.get("last_name", ""),
                        user.get("email", ""),
                    ]
                )
        print(f"List B saved to: {file_name_b}")

def generate_all_sponsor_csv():
    """Generates all the reports for every sponsor "detected" in the database"""        
    sponsor_emails = get_all_sponsor_events()
    if not sponsor_emails:
        print("No sponsor events found")
        return

    # Create reports directory once at the start
    os.makedirs(REPORTS_DIR, exist_ok=True)
    print(f"\nCreated reports directory: {REPORTS_DIR}")

    for sponsor in sponsor_emails:
        print(f"\nGenerating reports for {sponsor}")
        generate_report(sponsor)

    print(f"\nAll reports have been generated in: {REPORTS_DIR}")

if __name__ == "__main__":
    
    generate_all_sponsor_csv()
