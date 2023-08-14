from deep_translator import GoogleTranslator
import pandas as pd
import time

def translate_content(df, callback, num, file_location, num_to_translate, queue):
    # Create a new column for the translated text
    df['translated'] = ''
    
    # Iterate over the rows of the DataFrame
    for i, row in df.iterrows():
        # Get the language and content of the current row
        language = str(row['language'])
        content = str(row['content'])
        
        # Check if the language is not English and if the content has at least 3 characters
        if language != 'english' and len(content) >= 3:
            time.sleep(0.01)
            # Translate the content to English
            
            translated_text = GoogleTranslator(source=language, target='en').translate(content)
            # Store the translated text in the "translated" column
            df.at[i, 'translated'] = translated_text
        else:
            # Copy the content to the "translated" column
            df.at[i, 'translated'] = content
        
        callback((1/num_to_translate)*100)
    queue.put(df)
    #df.to_excel(f'{file_location}/{str(num)}.xlsx', sheet_name=str(num))
