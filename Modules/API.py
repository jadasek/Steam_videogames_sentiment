from transformers import AutoTokenizer, TFAutoModelForSequenceClassification, AutoModelForSequenceClassification
import numpy as np
import time

def spam_remover(df,queue,callback,total):
    tokenizer = AutoTokenizer.from_pretrained('distilbert-base-uncased')
    new_model = TFAutoModelForSequenceClassification.from_pretrained(
        "distilbert-base-uncased", num_labels=2
    )
    import os
    print(os.getcwd())
    new_model.load_weights(r"spam.h5")
    
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

        callback((1/total)*100,start_time-end_time)
    
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

    for i, row in df.iterrows():
        start_time = time.time()
        content = str(row['translated'])
        tweet = content

        # Sentiment analysis
        encoded_tweet = tokenizer(tweet, return_tensors='pt', max_length=512, truncation=True)
        output = model(**encoded_tweet)

        scores = output[0][0].detach().numpy()
        scores = softmax(scores)

        # Get the index of the highest score
        max_index = scores.argmax()

        # Get the label corresponding to the highest score
        predicted_sentiment = labels[max_index]

        # Store the predicted sentiment in the DataFrame
        df.at[i, 'predicted_sentiment'] = predicted_sentiment

        value = 0
        for score in range(len(scores)):
            if score == 1:
                value += scores[score] 
            elif score == 2:
                value += scores[score] * 2
        df.at[i, 'sentiment_value'] = value/2
        end_time = time.time()
        callback((1/total)*100, end_time-start_time)

    # Put the resulting DataFrame into the queue
    queue.put(df)

def summary(df,queue,callback,total):
    from transformers import pipeline
    from transformers import BertTokenizer
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    df['summary'] = ''
    for i, row in df.iterrows():
        start_time = time.time()
        content = str(row['translated'])
        if len(content) > 300:
            tokens = tokenizer.tokenize(content)
            num_tokens = len(tokens)
            summary = summarizer(content, max_length=min(int(num_tokens/2),1024), min_length=int(num_tokens/4), do_sample=False)[0]['summary_text']
            df.at[i, 'summary'] = summary
        else:
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
    for i, row in df.iterrows():
        start_time = time.time()
        content = str(row['translated'])
        sequence_to_classify = content
        result = classifier(sequence_to_classify, tags, multi_label=True)
        high_scores = [label for label, score in zip(result['labels'], result['scores']) if score > 0.75]
        df.at[i,'tags'] = high_scores
        end_time = time.time()
        callback((1/total)*100, end_time-start_time)

    queue.put(df)