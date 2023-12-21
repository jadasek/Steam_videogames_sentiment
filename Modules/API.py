from transformers import AutoTokenizer, TFAutoModelForSequenceClassification, AutoModelForSequenceClassification
import numpy as np
import time
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.dates import DateFormatter
from matplotlib.ticker import MaxNLocator
from reportlab.lib.pagesizes import landscape,A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

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

    print('LOK:',dname)
    new_model.load_weights(f"{dname}\spam.h5")
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

            if predicted_probabilities[0][1] >= 0.8:
                rows_to_remove.append(i)
        except:
            print(content)
            rows_to_remove.append(i)
        end_time = time.time()

        callback((1/total)*100,end_time-start_time)
    df.drop(rows_to_remove, inplace=True)
    df.reset_index(drop=True, inplace=True)
    queue.put(df)



def sentiment(df, queue, callback, total):
    from scipy.special import softmax
    roberta = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    model = AutoModelForSequenceClassification.from_pretrained(roberta)
    tokenizer = AutoTokenizer.from_pretrained(roberta)
    df['predicted_sentiment'] = ''
    df['sentiment_value'] = 0.0

    def sliding_window_sentiment(text, window_size, stride):
        values = []
        if len(text) < window_size:
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

def reporter(file_location, path,is_tagging,is_sentiment):
    if is_sentiment == True:
        matplotlib.use('agg')
        print('sentymuje')
        def add_numeric_annotations(ax):
            for bar in ax:
                yval = bar.get_height()
                plt.text(bar.get_x() + bar.get_width() / 2, yval + 0.1, round(yval, 1),
                        ha='center', va='bottom')


        df = pd.read_excel(file_location)
        df['date'] = pd.to_datetime(df['date'])
        df = df.dropna(subset=['date'])

        date_range = df["date"].max() - df["date"].min()
        if date_range.days > 180:
            time_interval = "M"
        elif date_range.days > 30:
            time_interval = "W"
        else:
            time_interval = "D"
        df_resampled = df.set_index("date").resample(time_interval).mean(numeric_only=True)

        plt.figure(figsize=(15,10))
        plt.plot(df_resampled.index, df_resampled["sentiment_value"], marker='o')
        plt.ylim(0, 1)
        plt.title("Zmiana sentymentu w czasie")
        plt.xlabel("Data")
        plt.ylabel("Wartość sentymentu")
        plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=6))  
        plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))  
        plt.grid(True)
        plt.savefig(f"{path}/sentiment_over_time.png")
        plt.close()

        sentiment_distribution = df["predicted_sentiment"].value_counts()
        plt.figure(figsize=(10, 6))
        ax_sentiment_distribution = sentiment_distribution.plot(kind='bar', color='skyblue')
        plt.title("Rozkład sentymentu")
        plt.xlabel("Sentyment")
        plt.ylabel("Liczba opinii")
        plt.xticks(rotation=0)  
        add_numeric_annotations(ax_sentiment_distribution.patches) 
        plt.savefig(f"{path}/sentiment_distribution_bar_chart.png")
        plt.close()
        if is_tagging == True:
            # Count the occurrences of each tag
            tag_counts = {}
            for tags in df["tags"]:
                if pd.notnull(tags):
                    tags_list = eval(tags)
                    for tag in tags_list:
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1


            plt.figure(figsize=(12, 8))  
            ax_tag_occurrences = plt.bar(tag_counts.keys(), tag_counts.values(), color='skyblue')
            plt.title("Występowanie tagów")
            plt.xlabel("Tag")
            plt.ylabel("Liczba opinii")
            plt.xticks(rotation=45, ha="right")  # Rotate x-axis labels for better visibility
            add_numeric_annotations(ax_tag_occurrences)  # Add numeric annotations
            plt.tight_layout()  # Adjust layout to prevent label cutting
            plt.savefig(f"{path}/tag_occurrences.png")
            plt.close()


        pdf_filename = f"{path}/raport.pdf"
        c = canvas.Canvas(pdf_filename, pagesize=landscape(A4))  

        c.setFont("Helvetica", 16)
        c.drawString(100, 750, "Raport")
        opinions_count = len(df)
        first_date = df["date"].min()
        last_date = df["date"].max()
        average_sentiment = df['sentiment_value'].mean()


        data = [
            ["Liczba opinii", opinions_count],
            ["Zakres dat", f"{first_date.strftime('%d.%m.%Y')} do {last_date.strftime('%d.%m.%Y')}"],
            ["Srednia wartosc sentymentu", round(average_sentiment, 2)],
        ]
        table = Table(data)
        table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                ]))
        table.wrapOn(c, 500, 400)
        table.drawOn(c, 280, 300)


        c.showPage()

        c.setFont("Helvetica", 14)
        c.drawString(100, 750, "Zmiana sentymentu w czasie")
        c.drawImage(f"{path}/sentiment_over_time.png", 50, 100, width=750, height=400) 
        c.showPage()

        c.setFont("Helvetica", 14)
        c.drawString(100, 750, "Summary Sentiment Distribution")
        c.drawImage(f"{path}/sentiment_distribution_bar_chart.png", 50, 100, width=750, height=400)  
        
        if is_tagging == True:
            c.showPage()
            c.setFont("Helvetica", 14)
            c.drawString(100, 750, "Występowanie tagów w opiniach")
            c.drawImage(f"{path}/tag_occurrences.png", 50, 100, width=750, height=400)  

        c.save()