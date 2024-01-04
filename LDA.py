# Code inspired by Kapadia, S. (2022, December 23). Topic Modeling in Python: Latent Dirichlet Allocation (LDA). Medium. https://towardsdatascience.com/end-to-end-topic-modeling-in-python-latent-dirichlet-allocation-lda-35ce4ed6b3e0 

# and

# Ruchirawat, N. (2020, October 31). 6 Tips for Interpretable Topic Models. Medium. https://towardsdatascience.com/6-tips-to-optimize-an-nlp-topic-model-for-interpretability-20742f3047e2 


# Preprocessing Step --------------------------------------------------------------------------

import pandas as pd
import re
import gensim
from gensim.utils import simple_preprocess
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
import gensim.corpora as corpora
import emoji
import os
from gensim.models import Phrases
import spacy

file_name = "Autism_Parenting_Venting-Needs-Support_Advice-Needed_no_comments(combined)"

file_path = 'data/'+file_name+'.csv'
df = pd.read_csv(file_path)

# Combine all the text for each document
df['combined_text'] = df['Title'].fillna('') + ' ' + df['Selftext'].fillna('') + ' ' + df['Comment'].fillna('')

# Remove punctuation
df['text_processed'] = \
df['combined_text'].map(lambda x: re.sub('[,\.!?]', '', x))

# Convert the titles to lowercase
df['text_processed'] = \
df['text_processed'].map(lambda x: x.lower())

# Remove emojis
df['text_processed'] = \
df['text_processed'].map(lambda x: emoji.demojize(x))

# Lemmatize sentences
nlp = spacy.load("en_core_web_sm")
lemmatizer = nlp.get_pipe("lemmatizer")

df['text_processed'] = \
df['text_processed'].map(lambda x: ' '.join([token.lemma_ for token in nlp(x)]))

stop_words = stopwords.words('english')
# stop_words.extend([])

def sentence_to_words(sentences):
    for sentence in sentences:
        yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))

def remove_stopwords(texts):
    return [[word for word in simple_preprocess(str(doc)) 
             if word not in stop_words] for doc in texts]

data = df.text_processed.values.tolist()
data_words = list(sentence_to_words(data))

# remove stop words
data_words = remove_stopwords(data_words)

# Create bigrams
bigram_phrases = Phrases(data_words, min_count=25, threshold=10)

# for bigram in bigram_phrases.export_phrases():
#     print(f"Bigram: {bigram}")

# Combine bigrams with unigrams
data_words = [bigram_phrases[line] for line in data_words]

# Create Dictionary
id2word = corpora.Dictionary(data_words)

# Create Corpus
texts = data_words

# Term Document Frequency
corpus = [id2word.doc2bow(text) for text in texts]

# Word Cloud -------------------------------------------------------

# Import the wordcloud library
from wordcloud import WordCloud

# Join the different processed titles together.
long_string = ','.join([' '.join(doc) for doc in data_words])

# Create a WordCloud object
wordcloud = WordCloud(background_color="white", max_words=1000, contour_width=3, contour_color='steelblue')

# Generate a word cloud
wordcloud.generate(long_string)

# Save the word cloud
os.makedirs('./results/'+file_name+'/', exist_ok=True)
wordcloud.to_file('./results/'+file_name+'/'+"wordcloud.png")


# Model Training ---------------------------------------------------

if __name__ == '__main__':
    from pprint import pprint

    # number of topics
    num_topics = 5

    # Build LDA model
    lda_model = gensim.models.LdaMulticore(corpus=corpus,
                                        id2word=id2word,
                                        num_topics=num_topics, 
                                        passes=320,
                                        iterations=200,  
                                        chunksize = 803,
                                        eval_every = 5,
                                        random_state=0)

    # Print the Keyword in the 10 topics
    # pprint(lda_model.print_topics())


    # Visualize Model

    import pyLDAvis.gensim_models as gensimvis
    import pickle 
    import pyLDAvis

    # Create the directory if it doesn't exist
    results_directory = './results/'+file_name+'/'
    os.makedirs(results_directory, exist_ok=True)

    LDAvis_data_filepath = os.path.join(results_directory, 'ldavis_prepared_'+str(num_topics))

    LDAvis_prepared = gensimvis.prepare(lda_model, corpus, id2word)
    with open(LDAvis_data_filepath, 'wb') as f:
        pickle.dump(LDAvis_prepared, f)

    # load the pre-prepared pyLDAvis data from disk
    with open(LDAvis_data_filepath, 'rb') as f:
        LDAvis_prepared = pickle.load(f)

    pyLDAvis.save_html(LDAvis_prepared, LDAvis_data_filepath +'.html')

    LDAvis_prepared