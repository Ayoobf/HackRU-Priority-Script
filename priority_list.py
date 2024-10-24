from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
import json

load_dotenv()


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

if __name__ == "__main__":
    # Get all sponsor emails
    sponsor_emails = get_all_sponsor_events()

    if sponsor_emails:
        # Get lists for each sponsor
        for sponsor_email in sponsor_emails:
            list_a, list_b = get_sponsor_list(sponsor_email)
            print(f"\nResults for {sponsor_email}:")
            if list_a:
                print("List A users:", [user["email"] for user in list_a])
            if list_b:
                print("List B users:", [user["email"] for user in list_b])
            print("-" * 50)
