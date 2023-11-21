import csv
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet.zip')
except LookupError:
    nltk.download('wordnet')

def preprocess_text(text):
    text = text.lower()

    text = re.sub(r'http\S+', '', text)

    tokens = word_tokenize(text)

    tokens = [word for word in tokens if word.isalnum()]

    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]

    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]

    processed_text = ' '.join(tokens)

    return processed_text


def build_comment_tree(csv_reader):
    comment_tree = {
        'text': 'Root',
        'score': None,
        'replies': []
    }

    previous_indentation = 0

    for row in csv_reader:
        current_submission = comment_tree
        title, selftext, comment_text, score = row
        indentation_level = int(len(comment_text) - len(comment_text.lstrip(' ')) / 2)
        
        if title != "":
            indentation_level += 1

        comment = {
            'text': preprocess_text(title) + preprocess_text(selftext) + preprocess_text(comment_text),
            'score': score,
            'replies': []
        }

        if indentation_level == 0:
            current_submission['replies'].append(comment)
            current_submission = comment
        elif indentation_level > previous_indentation:
            current_submission['replies'].append(comment)
            comment['parent'] = current_submission
            current_submission = comment
        else:
            for _ in range(previous_indentation - indentation_level + 1):
                current_submission = current_submission.get('parent', comment_tree)
            current_submission['replies'].append(comment)
            comment['parent'] = current_submission


        comment['parent'] = current_submission
        previous_indentation = indentation_level

    return comment_tree

comment_tree = None

csv_file_path = 'data/autism.csv'
with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
    csv_reader = csv.reader(csvfile)
    next(csv_reader)
    comment_tree = build_comment_tree(csv_reader)

    