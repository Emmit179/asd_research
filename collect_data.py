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

subreddit_name = 'Autism_Parenting'
subreddit = reddit.subreddit(subreddit_name)

num_posts_per_request = 100

allowed_flairs = ['Venting/Needs Support','Advice Needed']

include_comments = False

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

flair_str = '_'.join(flair.replace('/', '-').replace(' ', '-') for flair in allowed_flairs)
comments_str = 'with_comments' if include_comments else 'no_comments'
output_file = os.path.join(data_folder, f'{subreddit_name}_{flair_str}_{comments_str}(hot).csv')

after = None
old = 1

with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(['Title', 'Selftext', 'Comment', 'Score', 'Timestamp'])
    j = 0

    while True:
        print("after id: ", after)

        params = {'after': after} if after else {}

        submissions = subreddit.hot(limit=num_posts_per_request, params=params)

        if old == after:
            print("No more posts.")
            break

        old = after

        for submission in submissions:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(submission.created_utc))
            
            if submission.link_flair_text and submission.link_flair_text in allowed_flairs:
                csv_writer.writerow([
                    submission.title,
                    submission.selftext,
                    '',
                    submission.score,
                    timestamp,
                ])
                if include_comments:
                    process_comments(submission.comments, csv_writer)
                after = submission.fullname

                print("post: ", j)
                j += 1
                time.sleep(1)
