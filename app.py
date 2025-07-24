import pandas as pd
from datetime import datetime, timedelta

# Load the original CSV
df = pd.read_csv("Time-Off-Requests.csv")

# Convert 'Entitlement Used' to numeric hours
df["Entitlement Used"] = df["Entitlement Used"].str.replace(" Hours", "").astype(float)

# Convert Start and End to datetime
df["Start"] = pd.to_datetime(df["Start"], dayfirst=True)
df["End"] = pd.to_datetime(df["End"], dayfirst=True)

# Function to split entries into 12-hour days and max 48 hours per week
def split_entries(row):
    entries = []
    hours_remaining = row["Entitlement Used"]
    current_date = row["Start"].date()
    carer = row["Carer"]
    week_hours = {}

    while hours_remaining > 0:
        week_start = current_date - timedelta(days=current_date.weekday())  # Monday
        week_key = (carer, week_start)

        used_this_week = week_hours.get(week_key, 0)
        available_this_week = max(0, 48 - used_this_week)

        if available_this_week == 0:
            current_date += timedelta(days=1)
            continue
        hours_today = min(12, hours_remaining, available_this_week)
        start_dt = datetime.combine(current_date, datetime.min.time())
        end_dt = start_dt + timedelta(hours=hours_today)

        entries.append({
            "Carer": carer,
            "Start": start_dt.strftime("%d/%m/%Y %H:%M"),
            "End": end_dt.strftime("%d/%m/%Y %H:%M"),
            "Scheme": row["Scheme"],
            "Type": row["Type"],
            "Entitlement Used": hours_today,
            "Status": row["Status"]
        })

        week_hours[week_key] = week_hours.get(week_key, 0) + hours_today
        hours_remaining -= hours_today
        current_date += timedelta(days=1)

    return entries

# Apply the function to all rows
expanded_rows = []
for _, row in df.iterrows():
    expanded_rows.extend(split_entries(row))

# Create a new DataFrame and save to CSV
expanded_df = pd.DataFrame(expanded_rows)
expanded_df.to_csv("Expanded_Time_Off_Requests.csv", index=False)
