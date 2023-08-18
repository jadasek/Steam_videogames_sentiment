from deep_translator import GoogleTranslator
import pandas as pd
import time

def translate_large_text(text, source_lang, target_lang):
    # Set the maximum number of characters per chunk
    print('duży tekst')
    max_chars = 4999
    # Split the text into chunks
    chunks = [text[i:i+max_chars] for i in range(0, len(text), max_chars)]
    # Translate each chunk
    translated_chunks = [GoogleTranslator(source=source_lang, target=target_lang).translate(chunk) for chunk in chunks]
    # Concatenate the translated chunks
    translated_text = ''.join(translated_chunks)
    
    return translated_text

def translate_content(df, callback, num_to_translate, queue):
    # Create a new column for the translated text
    df['translated'] = ''
    
    # Iterate over the rows of the DataFrame
    for i, row in df.iterrows():
        start_time = time.time()
        # Get the language and content of the current row
        language = str(row['language'])
        content = str(row['content'])

        # Check if the language is not English and if the content has at least 3 characters
        if language != 'english' and len(content) >= 3:
            #time.sleep(0.05)
            # Translate the content to English using the translate_large_text function
            if len(content) >= 5000:
                try:
                    translated_text = translate_large_text(content, language, 'en')
                except:
                    for i in range(3):
                        try:
                            time.sleep(2)
                            translated_text = translate_large_text(content, language, 'en')
                            break
                        except:
                            pass
            else:
                try:
                    translated_text = GoogleTranslator(source=language, target='en').translate(content)
                except:
                    for i in range(3):
                        try:
                            time.sleep(2)
                            translated_text = GoogleTranslator(source=language, target='en').translate(content)
                            break
                        except:
                            pass
            # Store the translated text in the "translated" column
            df.at[i, 'translated'] = translated_text
        else:
            # Copy the content to the "translated" column
            df.at[i, 'translated'] = content

        end_time = time.time()
        
        callback((1/num_to_translate)*100,end_time-start_time)
    print('skończyłem translatować')
    queue.put(df)


