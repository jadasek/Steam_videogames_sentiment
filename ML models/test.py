from transformers import AutoTokenizer, TFAutoModelForSequenceClassification
import numpy as np


tokenizer = AutoTokenizer.from_pretrained('distilbert-base-uncased')
new_model = TFAutoModelForSequenceClassification.from_pretrained(
    "distilbert-base-uncased", num_labels=2
)
new_model.load_weights(r"C:\Users\tymot\Desktop\Projekty\Twitter_videogames_sentiment\ML models\spam.h5")
texts = ['asadasda', 'i like it', 'i think it"s ok']
for i in texts:
    test_texts = i
    encoded_test_texts = tokenizer(test_texts, padding=True, truncation=True)

    input_ids = np.array(encoded_test_texts['input_ids'])
    attention_mask = np.array(encoded_test_texts['attention_mask'])


    predictions = new_model.predict([input_ids, attention_mask])
    predicted_probabilities = np.array(predictions.logits)
    predicted_probabilities = np.exp(predicted_probabilities) / np.sum(np.exp(predicted_probabilities), axis=1, keepdims=True)

    print(f"Text: {test_texts}\nNot spam: {predicted_probabilities[0][0]}, Spam: {predicted_probabilities[0][1]}\n")
