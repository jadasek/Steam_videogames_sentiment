# %%
import tensorflow as tf 
from tensorflow.keras.preprocessing.text import Tokenizer 
from tensorflow.keras.preprocessing.sequence import pad_sequences 
import pandas as pd

data = pd.read_excel("export_dataframe_translated.xlsx")
data.info()

# %%
data = data.head(356)
display(data)

# %%
comments = data['content'] 
labels = data['opinion']

vocab_size = 40000
embedding_dim = 16
max_length = 120
trunc_type = 'post'
oov_tok = '<OOV>'
padding_type = 'post'

tokenizer = Tokenizer(num_words=vocab_size, oov_token=oov_tok)
tokenizer.fit_on_texts(comments)
word_index = tokenizer.word_index


sequences = tokenizer.texts_to_sequences(comments)
padded = pad_sequences(sequences, maxlen=max_length, truncating=trunc_type)
testing_sentences = tokenizer.texts_to_sequences(comments)
testing_padded = pad_sequences(testing_sentences, maxlen=max_length)


# %%
comments

# %%
print(testing_padded)

# %%
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(padded, labels, test_size=0.2, shuffle=True)

# %%
model = tf.keras.Sequential([
    tf.keras.layers.Embedding(vocab_size, embedding_dim,input_length=max_length),
    tf.keras.layers.GlobalAveragePooling1D(),
    tf.keras.layers.Dense(6, activation='relu'),
    tf.keras.layers.Dense(1, activation='sigmoid')
])

# %%
# Kompilowanie modelu 
import numpy as np
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
# Trenowanie modelu 
history = model.fit(X_train, y_train, epochs=20, validation_data=(testing_padded, labels))

# %%
y_test = list(y_test)
y_test = [int(x) for x in y_test]

# %%
predictions = model.predict(X_test)
predicted_labels = [1 if prediction > 0.5 else 0 for prediction in predictions]
suma = 0
for i in range(len(predicted_labels)):
    if predicted_labels[i] == y_test[i]:
        suma += 1

print(suma/len(predicted_labels))