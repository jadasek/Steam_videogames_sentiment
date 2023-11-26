from deep_translator import GoogleTranslator
import pandas as pd
import time

def translate_large_text(text, source_lang, target_lang):
    print('duży tekst')
    max_chars = 4999
    chunks = [text[i:i+max_chars] for i in range(0, len(text), max_chars)]
    translated_chunks = [GoogleTranslator(source=source_lang, target=target_lang).translate(chunk) for chunk in chunks]
    translated_text = ''.join(translated_chunks)
    return translated_text

def translate_content(df, callback, num_to_translate, queue):
    df['translated'] = ''
    for i, row in df.iterrows():
        start_time = time.time()
        language = str(row['language'])
        content = str(row['content'])
        if language != 'english' and len(content) >= 3:
            time.sleep(0.01)
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
            df.at[i, 'translated'] = translated_text
        else:
            df.at[i, 'translated'] = content
        end_time = time.time()
        callback((1/num_to_translate)*100,end_time-start_time)
    queue.put(df)


