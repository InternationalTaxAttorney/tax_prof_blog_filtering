import html
import os
import re
import smtplib
from datetime import datetime, timedelta

import feedparser
import pytz


def send_email(to: str, subj: str, body: str, attachment_path=None) -> None:
    app_password = os.environ.get("JJ_PW")
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    fromaddr = os.environ.get("JJ_EMAIL")
    toaddr = to
    msg = MIMEMultipart()
    msg["From"] = fromaddr
    msg["To"] = toaddr
    msg["Subject"] = subj
    msg.attach(MIMEText(body, "html"))
    email_content = msg.as_string()
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(fromaddr, app_password)
    server.sendmail(fromaddr, toaddr, email_content)
    server.quit()
    print("Email sent")


# convert the published date string into a datetime object
def parse_date(published_str):
    return datetime.strptime(published_str, "%a, %d %b %Y %H:%M:%S %z")


# feed_url = "https://feeds.feedburner.com/typepad/lFxP" # all posts
feed_url = "https://feeds.feedburner.com/typepad/ylQr"  # only tax posts

# Parse the RSS feed
feed = feedparser.parse(feed_url)

# Get the current time in UTC (offset-aware)
now = datetime.now(pytz.utc)

# Define a 7-day window
week_ago = now - timedelta(days=7)

titles_to_exclude = [
    "Tax Professor Rankings",
    "Weekend Roundup",
    "Most Popular TaxProf Blog Posts",
    "Call for Nominations",
    "Call for Papers",
    "Next Week’s Tax Workshops",
    "Income Inequality",
    "Tax Expenditures",
    "Subscribing To TaxProf Blog",
    "The 10 Most-Cited Tax Faculty",
    "The Top Five New Tax Papers",
    "Weekly SSRN Tax Article Review And Roundup",
    "Support TaxProf Blog",
    "Seeks To Hire",
    "is hiring",
    "Job Opening",
    "most downloaded",
    "Pepperdine",
]

# Regex patterns to exclude
patterns = [r"leaves .* for"]  # e.g., Victoria Haneman Leaves Creighton For Chair At Georgia

# Combine patterns with OR
combined_pattern = "|".join(patterns)

body = ""

# Iterate over each entry and filter those from the last 7 days
for entry in feed.entries:
    # Parse the published date
    published_date = parse_date(entry.published)

    if published_date >= week_ago:
        # get the title and remove html formatting
        title = html.unescape(entry.title)  # Titles might contain HTML entities (e.g., &amp; instead of &)
        title = title.replace("<strong>", "")
        title = title.replace("</strong>", "")
        title = title.replace("<em>", "")
        title = title.replace("</em>", "")

        link = entry.link
        published = published_date.strftime("%Y-%m-%d %H:%M:%S")

        if not any(title_to_exclude.lower() in title.lower() for title_to_exclude in titles_to_exclude):
            if not re.search(combined_pattern, title, re.IGNORECASE):
                body += f'<a href="{link}">{title}</a> ({published[0:10]})<br><br>'

send_email(os.environ.get("AM_EMAIL"), "TaxProfBlog Posts for the Week", body)
