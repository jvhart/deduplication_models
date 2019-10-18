
# =============================================================================
# Use pip install to install the packages below if they fail to import.  Some
# of these packages are automatically installed in Python distributions, others
# will require you to install by executing 'pip install (package name)'  in
# commend line.
# =============================================================================

import os # operating system interaction package
import re # regular expressions package
import pandas as pd # data storage, manipulation, and cleaning package
import numpy as np # vector and matrix compution package
import jellyfish # text distnace package
from scipy import sparse # sparse matrix representation and computation package
from itertools import product # product iteration function

# =============================================================================
# Set the root_dir variable to the local filepath where you have the repository.
# Check that you have the csv_example_messy_input.csv file in that folder.
# You can also modify the output filename to whatever you like.
# =============================================================================

root_dir = r'(filepath to deduplication_models repository)\deduplication_models\csv_example'
input_file = 'csv_example_messy_input.csv'
output_file = 'csv_example_record_key.csv'

# =============================================================================
# Below are severl functions that will be used in the deduplication.
# =============================================================================

def clean_site_name(s):
    '''
    Funcation made to clean site names.
    It removes all special characters, levaing only alphanumeric values and spaces.
    Special characters are replaced with spaces.
    Leading and trailing spaces are removed.
    All multiple spaces are reduced to a single space between words.
    '''
    s = re.sub(r'([^\s\w]|_)+',' ',s.lower()).strip()
    l = len(s) + 1
    while l > len(s):
        l = len(s)
        s = s.replace('  ',' ')
    return s

def site_name_distance(x,y):
    '''
    This is the distance function to be used for site name comparisons.
    It splits the cleaned site name into words, and computes the one-way metric engulfing based on the Levenshtein distance
    '''
    X = x.split(' ')
    Y = y.split(' ')
    A = np.zeros((len(X),len(Y)))
    for i in range(len(X)):
        for j in range(len(Y)):
            A[i,j] = jellyfish.levenshtein_distance(X[i],Y[j])
    return min([A.min(0).sum(),A.min(1).sum()])

def clean_address(s):
    '''
    Funcation made to clean addresses.
    It removes all special characters, levaing only alphanumeric values and spaces.
    Special characters are replaced with spaces.
    It also replaces typical street types and abbreviation, replacing them with spaces.
    All multiple spaces are reduced to a single space between words.
    Leading and trailing spaces are removed.
    '''
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

def address_distance(x,y):
    '''
    This is the distance function to be used for address comparisons.
    It splits the cleaned address into words, and computes the one-way metric engulfing based on the Levenshtein distance
    '''
    X = x.split(' ')
    Y = y.split(' ')
    A = np.zeros((len(X),len(Y)))
    for i in range(len(X)):
        for j in range(len(Y)):
            A[i,j] = jellyfish.levenshtein_distance(X[i],Y[j])
    return min([A.min(0).sum(),A.min(1).sum()])

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

def phone_distance(x,y):
    '''
    This is the distance function to be used for phone number comparisons.
    It computes the Levenstein distance for each section of the phone number
    '''
    dist = 0
    if x[0] is None or y[0] is None:
        dist += .25
    else:
        dist += jellyfish.levenshtein_distance(x[0],y[0])

    if x[1] is None or y[1] is None:
        dist += 1
    else:
        dist += jellyfish.levenshtein_distance(x[1],y[1])

    if x[2] is None or y[2] is None:
        dist += .5
    else:
        dist += jellyfish.levenshtein_distance(x[2],y[2])
    return dist

# =============================================================================
# Here starts the actual reading, cleaning, analysis, and record deduplication
# of the data.
# =============================================================================

# Import data source as a dataframe using pandas read_csv function
df = pd.read_csv(os.path.join(root_dir,input_file))

# Clean addresses, names, zip codes, and phone numbers
df['Address clean'] = df['Address'].apply(clean_address)
df['Site name clean'] = df['Site name'].apply(clean_site_name)
df['Zip clean'] = df['Zip'].apply(lambda x : str(int(x)).zfill(5) if pd.notna(x) else None)
df['Phone parsed'] = df['Phone'].apply(clean_phone)
df['Phone clean'] = df['Phone parsed'].apply(lambda p : '-'.join([ x for x in p if x is not None]))

# Reset the index of the dataframe as the Id from the dataset
df.index = df['Id']

# Initialize an empty dataframe to store the duplicate graph information and a dedup graph id
dedup_graph_df = pd.DataFrame(columns=['row','column','block_type','block_value','diameter'])
dedup_graph_id = 0

# Compute a dataframe indexed by zip code, with lists of Ids inside that zip code.
# You'll note that this computation contains an oversite.  Entries without a
# zip code are excluded entirely.  This should be addressed.
zip_blocks = df[['Id','Zip clean']].groupby('Zip clean').agg({'Id' : list})

# Deduplication threshold and weights for weighted distance.
# These values should be adjusted based on performance or optimzed with respect
# to a training set.
threshold = 1.5
weights = {'site_name' : .5,
           'address' : .75,
           'phone' : .25}

for zip_code,d in zip_blocks.iterrows(): # This loop iterates over deduplication blocks (zip codes)
    ids = d['Id'] # list of Ids inside the given zip code
    A = np.zeros((len(ids),len(ids))) # initialize 'distance' matrix
    if len(ids) > 1:
        for i, id_i in zip(range(len(ids)),ids): # Compute distance matrix
            d_i = df.loc[id_i,:]
            for j, id_j in zip(range(i),ids):
                d_j = df.loc[id_j,:]
                site_name_dist = site_name_distance(d_i['Site name clean'],d_j['Site name clean'])
                address_dist = address_distance(d_i['Address clean'],d_j['Address clean'])
                phone_dist = phone_distance(d_i['Phone parsed'],d_j['Phone parsed'])
                A[i,j] = weights['site_name'] * site_name_dist + weights['address'] * address_dist + weights['phone'] * phone_dist
                A[j,i] = A[i,j]
    AA = (A <= threshold) * 1 # apply threshold to make dedup graph adjacency matrix
    num_classes,class_map = sparse.csgraph.connected_components(AA,directed = False) # estract connected components
    clusters = [ list(np.where(class_map == i)[0]) for i in range(num_classes) if len(np.where(class_map == i)[0]) > 1] # extract clusters
    cluster_diameters = [max([A[i,j] for i,j in product(c,c)]) for c in clusters] # compute cluster diameter

    for c,d in zip(clusters,cluster_diameters): # loop through new duplicate records and append to dedup_graph_df
        for i,j in zip(c[:-1],c[1:]):
            new_row = pd.Series({'row' : ids[i],
                                 'column' : ids[j],
                                 'block_type' : 'zip_code',
                                 'block_value' : zip_code,
                                 'diameter' : d
                                 })
            new_row.name = dedup_graph_id
            dedup_graph_id += 1
            dedup_graph_df = dedup_graph_df.append(new_row)

# Exctract clusters from full dedup graph
dedup_graph = sparse.csr_matrix(([1] * len(dedup_graph_df), (dedup_graph_df['row'].tolist(), dedup_graph_df['column'].tolist())), shape=(len(df), len(df)))
num_classes,class_map = sparse.csgraph.connected_components(dedup_graph,directed = False)
clusters = [list(np.where(class_map == i)[0]) for i in range(num_classes) if len(np.where(class_map == i)[0]) > 1]

# Create a map from record Id to a cluster_id, to become the golden record id
cluster_map = {}
cluster_id = 0
for c in clusters: # map all records for which duplicates were discovered
    cluster_map.update({ind : cluster_id for ind in c})
    cluster_id += 1

all_dedup_ids = list(cluster_map.keys())
for ind in df['Id']: # map all records for which no duplicates were discovered
    if not ind in all_dedup_ids:
        cluster_map.update({ind : cluster_id})
        cluster_id += 1

# append golden record id to the dataset
df['Golden record id'] = df['Id'].apply(lambda x : cluster_map[x])

# create key between source and golden record, write it to a csv file
record_key = df[['Golden record id','Id']].rename(columns = {'Id' : 'src_id', 'Golden record id' : 'gld_id'})
record_key.to_csv(os.path.join(root_dir,output_file),index=False)

# =============================================================================
# Below is a few lines of code to review the results.  Set a golden record key
# and run the following lines to display the associate records that have been
# deduplicated.
# =============================================================================

for gld_rec_key in range(150):
    temp = df[df['Golden record id'] == gld_rec_key].copy()

    print('\n\n{} duplicate records discovered for golden record key {}'.format(len(temp),gld_rec_key))
    print('\nSite names:')
    print(temp['Site name'])
    print('\nAddresses:')
    print(temp['Address'])
    print('\nZip codes:')
    print(temp['Zip clean'])
    print('\nPhone numbers:')
    print(temp['Phone clean'])

    s = input('Press enter to see another, enter "q" to quit: ')
    if s == 'q':
        break
