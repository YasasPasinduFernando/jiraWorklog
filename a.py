import requests
import datetime
import pandas as pd
from base64 import b64encode

# === CONFIGURATION ===
EMAIL = "pasindu.fernando@ideahub.lk"
API_TOKEN = ""
JIRA_DOMAIN = "https://ideahubsupport.atlassian.net"

# === DATE RANGE ===
today = datetime.date.today()
start_date = today - datetime.timedelta(days=31)
start_str = start_date.isoformat()

# === AUTH HEADER ===
auth_str = f"{EMAIL}:{API_TOKEN}"
auth_bytes = b64encode(auth_str.encode()).decode("utf-8")
headers = {
    "Authorization": f"Basic {auth_bytes}",
    "Content-Type": "application/json"
}

# === Get your own accountId first ===
me_url = f"{JIRA_DOMAIN}/rest/api/3/myself"
me_resp = requests.get(me_url, headers=headers)
my_account_id = me_resp.json()["accountId"]

# === JQL ===
jql = f"worklogAuthor = currentUser() AND worklogDate >= {start_str}"
search_url = f"{JIRA_DOMAIN}/rest/api/3/search"
params = {
    "jql": jql,
    "maxResults": 100,
    "fields": "summary,worklog"
}

response = requests.get(search_url, headers=headers, params=params)
data = response.json()

worklogs = []

for issue in data.get("issues", []):
    key = issue["key"]
    summary = issue["fields"]["summary"]
    worklog_entries = issue["fields"]["worklog"]["worklogs"]

    for log in worklog_entries:
        # Now check by accountId instead of email
        if log["author"]["accountId"] == my_account_id:
            date = log["started"].split("T")[0]
            time_sec = log["timeSpentSeconds"]
            worklogs.append({
                "Issue": key,
                "Summary": summary,
                "Date": date,
                "Time (hours)": round(time_sec / 3600, 2)
            })

# === EXPORT TO CSV OR PRINT ===
df = pd.DataFrame(worklogs)
df_grouped = df.groupby("Date").sum().reset_index()
print(df_grouped)

# Optionally save to Excel
df_grouped.to_excel("my_jira_worklogs.xlsx", index=False)
