# HackRU Priority Lists Generator

A Python script to generate priority lists (A/B) for HackRU sponsors based on QR code scans.

## Overview

This script processes HackRU sponsor scanning data and generates CSV files containing attendee information for each sponsor's A and B priority lists. Each sponsor can scan attendees' QR codes and assign them to either list A or list B.

## Prerequisites

- Python 3.9 or higher
- MongoDB connection string
- Access to HackRU's database

## Installation

1. Clone the repository:
```bash
git clone https://github.com/HackRU/sponsor-priority-lists.git
cd sponsor-priority-lists
```

2. Create a virtual environment:
```bash
python -m venv venv

# On Windows
.\venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file:
```env
MONGO_URI="your_mongodb_connection_string"
DB_NAME="your_database_name"
```

## Usage

### Basic Usage
```bash
python priority_list.py
```

This will:
1. Connect to MongoDB
2. Find all sponsor events
3. Generate CSV files for each sponsor's A and B lists
4. Save files in a timestamped directory (e.g., `reports_20241024_143000`)

### Output Format

The script creates a new directory for each run with the format `reports_YYYYMMDD_HHMMSS/`:
```
reports_20241024_143000/
├── priority_list_sponsor1_a.csv
├── priority_list_sponsor1_b.csv
├── priority_list_sponsor2_a.csv
└── priority_list_sponsor2_b.csv
```

Each CSV contains:
- First Name
- Last Name
- Email

## Data Structure

The script looks for sponsor scanning data in this MongoDB structure:
```json
{
  "day_of": {
    "event": {
      "sponsor1@company.com": {    <--- Searches for this sponsor email, Sponsor1
        "orgSponsorB": {           <--- Puts this user in the B list of sponsor1
          "attend": 1,
          "time": ["timestamp"]
        }
      },"sponsor2@company.com": {  <--- Sponsor2
        "orgSponsorA": {           <--- Puts the user in the A list of sponsor2
          "attend": 1,
          "time": ["timestamp"]
        }
      }
    }
  }
}
```
