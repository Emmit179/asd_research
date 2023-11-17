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

num_posts_per_request = 1000  
num_requests = 60  

def process_comments(comments, csv_writer, indentation_level=0):
    for comment in comments:
        if isinstance(comment, praw.models.MoreComments):
            continue
        
        if not comment.is_root:
            continue
 
        csv_writer.writerow(['', '', '  ' * indentation_level + comment.body])
      
        process_comments(comment.replies, csv_writer, indentation_level + 1)

after = None

output_file = 'reddit_data.csv'

with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    
    csv_writer = csv.writer(csvfile)

    csv_writer.writerow(['Title', 'Selftext', 'Comment'])
    
    for _ in range(num_requests):
        
        submissions = subreddit.search(query="*", sort='new', limit=num_posts_per_request, params={'after': after})
        
        for submission in submissions:
            
            csv_writer.writerow([submission.title, submission.selftext, ''])
            
            process_comments(submission.comments, csv_writer)
            
            after = submission.name
            
            time.sleep(2)