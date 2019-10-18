
# =============================================================================
# Use pip install to install the packages below if they fail to import.  Some
# of these packages are automatically installed in Python distributions, others
# will require you to install by executing 'pip install (package name)'  in
# commend line.
# =============================================================================

import os
import re
import pandas as pd
from matplotlib import pyplot as plt
from collections import Counter

# =============================================================================
# Set the root_dir variable to the local filepath where you have the repository.
# Check that you have the csv_example_messy_input.csv file in that folder.
# =============================================================================

root_dir = r'(filepath to deduplication_models repository)\deduplication_models\csv_example'
input_file = 'csv_example_messy_input.csv'

def clean_site_name(s):
    '''
    Funcation made to clean site names.  It removes all special characters, levaing only alphanumeric values and spaces.
    Special characters are replaced with spaces.
    Leading and trailing spaces are removed.
    All multiple spaces are reduced to a single space between words.
    '''
    s = re.sub(r'([^\s\w]|_)+',' ',s.lower()).strip()  # keep only alphanumeric and spaces
    l = len(s) + 1
    while l > len(s):                         # reduce any multiple spaces to a single space
        l = len(s)
        s = s.replace('  ',' ')
    return s

def clean_address(s):
    s = re.sub(r'([^\s\w]|_)+',' ',s.lower()).join([' ',' '])  # keep only alphanumeric and spaces
    replace_dict = {' st ' : ' ',
                    ' rd ' : ' ',
                    ' ave ' : ' ',
                    ' ct ' : ' ',
                    ' dr ' : ' ',
                    ' pl ' : ' ',
                    ' blvd ' : ' ',
                    ' street ' : ' ',
                    ' road ' : ' ',
                    ' avenue ' : ' ',
                    ' court ' : ' ',
                    ' drive ' : ' ',
                    ' place ' : ' ',
                    ' terrace ' : ' ',
                    ' boulevard ' : ' ',
                    ' north ' : ' n ',
                    ' south ' : ' s ',
                    ' east ' : ' e ',
                    ' west ' : ' w ',
                    }
    for k,v in replace_dict.items():
        s = s.replace(k,v)
    l = len(s) + 1
    while l > len(s):                         # reduce any multiple spaces to a single space
        l = len(s)
        s = s.replace('  ',' ')
    return s.strip()

searcher = re.compile(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})')

def clean_phone(x):
    try:
        x = str(int(x))
        a = searcher.match(x.replace('/','').replace('-','').replace('(','').replace(')','').replace(' ','').replace('.',''))
        phone = a[0]
    except:
        return (None,None,None)
    if len(phone) == 11:
        return (phone[1:4],phone[4:7],phone[7:11])
    if len(phone) == 10:
        return (phone[:3],phone[3:6],phone[6:10])
    elif len(phone) == 7:
        return (None,phone[:3],phone[3:7])
    else:
        return (None,None,None)

# Import data source as a dataframe using pandas read_csv function
df = pd.read_csv(os.path.join(root_dir,input_file))

# print the column names of the dataframe
print(df.columns)

# missing values by column
print(df.isna().any())

# number of missing values by column
print((df.isna() * 1).sum())

# proportion of missing values by column
print((df.isna() * 1).sum() / len(df))

# Clean addresses, names, zip codes, and phone numbers
df['Address clean'] = df['Address'].apply(clean_address)
df['Site name clean'] = df['Site name'].apply(clean_site_name)
df['Zip clean'] = df['Zip'].apply(lambda x : str(int(x)).zfill(5) if pd.notna(x) else None)
df['Phone parsed'] = df['Phone'].apply(clean_phone)
df['Phone clean'] = df['Phone parsed'].apply(lambda p : '-'.join([ x for x in p if x is not None]))

# Below are frequency plots of words appearing addresses, words in site names,
# and zip codes in the data set.
# Looking closer at these kinds of plots can help to build a better cleaning
# process, comparison metric, or deduplication criteria.

address_words = []
for addr in df['Address clean']:
    addr_words = addr.split(' ')
    address_words += [w for w in addr_words if not w.isdigit()]
address_word_count = Counter(address_words)
top_n_plot = 40
plt.figure(figsize=(18,10))
plt.bar([w for w,c in address_word_count.most_common(top_n_plot) if w is not None],[c for w,c in address_word_count.most_common(top_n_plot) if w is not None])
plt.xticks(rotation=90,fontsize=16)
plt.title('Top {} address word frequency'.format(top_n_plot),fontsize=24)
plt.show()


all_site_name_words = []
for i,d in df.iterrows():
    all_site_name_words += d['Site name clean'].split(' ')
site_word_count = Counter(all_site_name_words)
top_n_plot = 25
plt.figure(figsize=(18,10))
plt.bar([w for w,c in site_word_count.most_common(top_n_plot)],[c for w,c in site_word_count.most_common(top_n_plot)])
plt.xticks(rotation=90,fontsize=16)
plt.title('Top {} site name word frequency'.format(top_n_plot),fontsize=24)
plt.show()


zip_code_count = Counter(df['Zip clean'].tolist())
top_n_plot = 40
plt.figure(figsize=(18,10))
plt.bar([w for w,c in zip_code_count.most_common(top_n_plot) if w is not None],[c for w,c in zip_code_count.most_common(top_n_plot) if w is not None])
plt.xticks(rotation=90,fontsize=16)
plt.title('Top {} zip codes'.format(top_n_plot),fontsize=24)
plt.show()
