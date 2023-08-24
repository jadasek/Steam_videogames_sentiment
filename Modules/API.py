from transformers import AutoTokenizer, TFAutoModelForSequenceClassification, AutoModelForSequenceClassification
import numpy as np
import time
import os



def spam_remover(df,queue,callback,total):
    abspath = os.path.abspath(__file__)
    print(f'abspath: {abspath}')
    dname = os.path.dirname(abspath)
    print(f'dname: {dname}')
    os.chdir(dname)
    tokenizer = AutoTokenizer.from_pretrained('distilbert-base-uncased')
    new_model = TFAutoModelForSequenceClassification.from_pretrained(
        "distilbert-base-uncased", num_labels=2
    )

    print(os.getcwd())
    new_model.load_weights(f"{dname}\spam.h5")
    
    # Create a list to store the indices of rows to be removed
    rows_to_remove = []

    for i, row in df.iterrows():
        start_time = time.time()
        content = str(row['translated'])
        test_texts = content
        encoded_test_texts = tokenizer(test_texts, padding=True, truncation=True, max_length=1024)

        input_ids = np.array(encoded_test_texts['input_ids'])
        attention_mask = np.array(encoded_test_texts['attention_mask'])
        try:
            predictions = new_model.predict([input_ids, attention_mask])
            predicted_probabilities = np.array(predictions.logits)
            predicted_probabilities = np.exp(predicted_probabilities) / np.sum(np.exp(predicted_probabilities), axis=1, keepdims=True)

            # Check if the probability of the text being spam is greater than or equal to 0.8
            if predicted_probabilities[0][1] >= 0.8:
                # Add the index of the row to the list of rows to be removed
                rows_to_remove.append(i)
        except:
            print(content)
            rows_to_remove.append(i)
        end_time = time.time()

        callback((1/total)*100,end_time-start_time)
    
    # Remove the rows from the dataframe
    df.drop(rows_to_remove, inplace=True)
    
    # Reset the index of the dataframe
    df.reset_index(drop=True, inplace=True)
    
    # Put the resulting dataframe back into the queue
    queue.put(df)



def sentiment(df, queue, callback, total):
    from scipy.special import softmax
    roberta = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    model = AutoModelForSequenceClassification.from_pretrained(roberta)
    tokenizer = AutoTokenizer.from_pretrained(roberta)
    labels = ['Negative', 'Neutral', 'Positive']

    # Create a new column in the DataFrame to store the predicted sentiment
    df['predicted_sentiment'] = ''
    df['sentiment_value'] = 0.0

    def sliding_window_sentiment(text, window_size, stride):
        sentiments = []
        values = []
        if len(text) < window_size:
            # Handle the case where the text is shorter than the window size
            encoded_tweet = tokenizer(text, return_tensors='pt', max_length=512, truncation=True)
            output = model(**encoded_tweet)
            scores = output[0][0].detach().numpy()
            scores = softmax(scores)

            value = 0
            for score in range(len(scores)):
                if score == 1:
                    value += scores[score] 
                elif score == 2:
                    value += scores[score] * 2
            values.append(value/2)
            
        else:
            start = 0
            end = window_size
            while end <= len(text):
                chunk = text[start:end]
                encoded_tweet = tokenizer(chunk, return_tensors='pt', max_length=512, truncation=True)
                output = model(**encoded_tweet)
                scores = output[0][0].detach().numpy()
                scores = softmax(scores)

                value = 0
                for score in range(len(scores)):
                    if score == 1:
                        value += scores[score] 
                    elif score == 2:
                        value += scores[score] * 2
                values.append(value/2)

                start += stride
                end += stride

        return sum(values)/len(values)

    for i, row in df.iterrows():
        start_time = time.time()
        try:
            content = str(row['translated'])
            tweet = content

            # Sentiment analysis
            if len(content) > 500:
                window_size = 1024
                stride = 1024
                sentiment_value = sliding_window_sentiment(tweet, window_size, stride)
                df.at[i, 'sentiment_value'] = sentiment_value

                if sentiment_value < 0.15:
                    predicted_sentiment = 'Very negative'
                elif sentiment_value < 0.30:
                    predicted_sentiment = 'Negative'
                elif sentiment_value < 0.7:
                    predicted_sentiment = 'Neutral'
                elif sentiment_value < 0.85:
                    predicted_sentiment = 'Positive'
                else:
                    predicted_sentiment = 'Very positive'

                df.at[i, 'predicted_sentiment'] = predicted_sentiment
            else:
                encoded_tweet = tokenizer(tweet, return_tensors='pt', max_length=512, truncation=True)
                output = model(**encoded_tweet)
                scores = output[0][0].detach().numpy()
                scores = softmax(scores)

                value = 0
                for score in range(len(scores)):
                    if score == 1:
                        value += scores[score] 
                    elif score == 2:
                        value += scores[score] * 2
                df.at[i, 'sentiment_value'] = value/2

                value = value/2
                
                if value < 0.15:
                    predicted_sentiment = 'Very negative'
                elif value < 0.30:
                    predicted_sentiment = 'Negative'
                elif value < 0.7:
                    predicted_sentiment = 'Neutral'
                elif value < 0.85:
                    predicted_sentiment = 'Positive'
                else:
                    predicted_sentiment = 'Very positive'
                
                df.at[i, 'predicted_sentiment'] = predicted_sentiment
        except:
            df.at[i, 'sentiment_value'] = 'ERROR'
        end_time = time.time()
        callback((1/total)*100, end_time-start_time)


    # Put the resulting DataFrame into the queue
    queue.put(df)

def summary(df,queue,callback,total):
    from transformers import pipeline
    from transformers import BertTokenizer
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    def sliding_window_summarize(text, window_size, stride):
        print('użyto sliding window')
        summaries = []
        start = 0
        end = window_size
        while end <= len(text):
            chunk = text[start:end]
            tokens = tokenizer.tokenize(chunk)
            num_tokens = len(tokens)
            summary = summarizer(chunk, max_length=min((num_tokens/2),100), min_length=15)[0]['summary_text']
            summaries.append(summary)
            start += stride
            end += stride
        return ' '.join(summaries)

    df['summary'] = ''
    for i, row in df.iterrows():
        start_time = time.time()
        try:
            content = str(row['translated'])
            if len(content) > 500:
                window_size = 1024
                stride = 1024
                summary = sliding_window_summarize(content, window_size, stride)
                df.at[i, 'summary'] = summary
            else:
                df.at[i, 'summary'] = ' '
        except:
                df.at[i, 'summary'] = ' '
        end_time = time.time()
        callback((1/total)*100, end_time-start_time)

    queue.put(df)


def tagger(df,queue,callback,total,tags):
    tags = tags.replace("\n", ",")
    tags = [x for x in tags.split(",") if x]
    from transformers import pipeline
    df['tags'] = ''

    classifier = pipeline("zero-shot-classification",
                      model="MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli")

    def sliding_window_classify(text, window_size, stride):
        classifications = []
        start = 0
        end = window_size
        while end <= len(text):
            chunk = text[start:end]
            result = classifier(chunk, tags, multi_label=True)
            high_scores = [label for label, score in zip(result['labels'], result['scores']) if score > 0.75]
            classifications.extend(high_scores)
            start += stride
            end += stride
        return list(set(classifications))

    for i, row in df.iterrows():
        start_time = time.time()
        content = str(row['translated'])
        try:
            if len(content) >= 150:
                if len(content) > 1000:
                    window_size = 1024
                    stride = 512
                    classifications = sliding_window_classify(content, window_size, stride)
                    df.at[i,'tags'] = classifications
                else:
                    sequence_to_classify = content
                    result = classifier(sequence_to_classify, tags, multi_label=True)
                    high_scores = [label for label, score in zip(result['labels'], result['scores']) if score > 0.75]
                    df.at[i,'tags'] = high_scores
            else:
                df.at[i,'tags'] = []
        except:
            df.at[i,'tags'] = []
        end_time = time.time()
        callback((1/total)*100, end_time-start_time)

    queue.put(df)

