# %%
import pandas as pd
import translators as ts
from tqdm.notebook import tqdm
import time

data = pd.read_excel("export_dataframe.xlsx")
#display(data)
for i in tqdm(range(len(data.index))):
    if data.iloc[i]['language'] != 'en':
        data.at[i, 'content'] = ts.translate_text(data.iloc[i]['content'], to_language='en', translator='google')
        time.sleep(0.1)
display(data)

data.to_excel('export_dataframe_translated.xlsx', index=False)
