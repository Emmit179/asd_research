import praw
import csv
import time
from dotenv import load_dotenv
import os

load_dotenv('.env')

client_id = os.getenv('API_KEY')
client_secret = os.getenv('API_SECRET')
user_agent = os.getenv('API_AGENT')

reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent=user_agent
)

subreddit_name = 'autism'
subreddit = reddit.subreddit(subreddit_name)

num_posts_per_request = 100

def process_comments(comments, csv_writer, indentation_level=0):
    for comment in comments:
        if isinstance(comment, praw.models.MoreComments):
            continue

        if comment.author and comment.author.name == "AutoModerator":
            continue

        csv_writer.writerow([
            '', 
            '', 
            '  ' * indentation_level + comment.body,
            comment.score,
        ])
      
        process_comments(comment.replies, csv_writer, indentation_level + 1)

data_folder = 'data'
os.makedirs(data_folder, exist_ok=True)

output_file = os.path.join(data_folder, subreddit_name+'.csv')

after = None
old = 1

with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(['Title', 'Selftext', 'Comment', 'Score'])
    j = 0

    while True:
        print("after id: ", after)

        params = {'after': after} if after else {}

        submissions = subreddit.new(limit=num_posts_per_request, params=params)

        if old == after:
            print("No more posts.")
            break

        old = after

        for submission in submissions:
            csv_writer.writerow([
                submission.title,
                submission.selftext,
                '',
                submission.score,
            ])
            process_comments(submission.comments, csv_writer)
            after = submission.fullname

            print("post: ", j)
            j += 1
            time.sleep(1)