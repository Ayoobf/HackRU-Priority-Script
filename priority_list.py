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


def get_sponsor_list():
    """
    Gets the list of users scanned by sponsors
    Returns two lists: A (regular) and B (special)
    """
    db = connect_to_mongodb()
    if db is None:
        return None, None

    try:
        users = db["users"]

        # The correct syntax is $exists instead of exists
        sponsor_a_users = list(
            users.find(
                {"day_of.event.SponsorA.attend": {"$exists": True}},
                {
                    "email": 1,
                    "first_name": 1,
                    "last_name": 1,
                    "day_of.event.SponsorA.time": 1,
                    "_id": 0,
                },
            )
        )

        # Corrected the path for sponsor B based on your MongoDB structure
        sponsor_b_users = list(
            users.find(
                {"day_of.event.organizer@test.orgSponsorB.attend": {"$exists": True}},
                {
                    "email": 1,
                    "first_name": 1,
                    "last_name": 1,
                    "day_of.event.organizer@test.orgSponsorB.time": 1,
                    "_id": 0,
                },
            )
        )

        print(f"Found {len(sponsor_a_users)} users in Sponsor A list")
        print(f"Found {len(sponsor_b_users)} users in Sponsor B list")

        # Print first user from each list for debugging
        if sponsor_a_users:
            print("\nFirst user in Sponsor A list:", sponsor_a_users[0])
        if sponsor_b_users:
            print("\nFirst user in Sponsor B list:", sponsor_b_users[0])

        return sponsor_a_users, sponsor_b_users

    except Exception as e:
        print(f"Error in get_sponsor_list: {e}")
        return None, None


if __name__ == "__main__":
    # Add some debug prints
    print("Connecting to MongoDB...")
    db = connect_to_mongodb()
    if db is None:
        print("Successfully connected to MongoDB")
        # Print all collection names
        print("Available collections:", db.list_collection_names())

    # Get sponsor lists
    sponsor_a, sponsor_b = get_sponsor_list()

    # Print complete results
    if sponsor_a or sponsor_b:
        print("\nComplete Results:")
        print(f"Sponsor A list ({len(sponsor_a) if sponsor_a else 0} users):")
        for user in sponsor_a or []:
            print(
                f"- {user.get('email')}: {user.get('first_name')} {user.get('last_name')}"
            )

        print(f"\nSponsor B list ({len(sponsor_b) if sponsor_b else 0} users):")
        for user in sponsor_b or []:
            print(
                f"- {user.get('email')}: {user.get('first_name')} {user.get('last_name')}"
            )
