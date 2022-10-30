import pandas as pd
import re
from collections import Counter
import sqlite3

# Load the Wikipedia dataset ("wikipedia_dataset.xlsx") into a Pandas dataframe and view it
# 1. Download the Wikipedia data
# 2. Take a look at the first 10 entries

Wikipedia_2016 = pd.read_excel("wikipedia_dataset.xlsx")
display(Wikipedia_2016.head(10))

# Print out some basic information about the dataframe

print(Wikipedia_2016.info(verbose = True))

# Our table has 1500 rows and 367 columns. To make working with the data easier, it will be best to reshape it so that there are fewer columns.
# using pandas .melt(), unpivot the Wikipedia_2016 dataframe

Melted_Wikipedia = pd.melt(Wikipedia_2016, id_vars= "Page", var_name= "Date", value_name= "Visits")
print(Melted_Wikipedia.head())


# Check the shape of our melted dataframe

Melted_Wikipedia.shape

# At this point, we would want to know if our dataset contains any duplicate rows or missing values
# Check for contains duplicate entries

Melted_Wikipedia.duplicated().sum()
# Check for missing values
Melted_Wikipedia.isnull().sum()

# The next few steps would involve some feature engineering that is necessary to enable us answer the given questions
# 1. Add a column that tells us what day of the week a webpage was visited
# 2. A column with the information on the language a page was written in
# 3. What device was used in a search

# 1. Create a new column "Day" whose value is the day of the week a search occured

Melted_Wikipedia['Day'] = pd.to_datetime(Melted_Wikipedia['Date']).dt.day_name()
Melted_Wikipedia.head()

# A column for languages;
# One may infer which language a page is written in based on the page name
# e.g. Special:Search_fr.wikipedia.org_all-access_all-agents is written in French and Special:Book_en.wikipedia.org_all-access_spider is written in English.

# 2a. Using .search() method of the Regex module, define a function that returns the 2 letters that represent the langauge of the page (eg., en for English), or "na" if language is not found
# 2b. Use .map() to call the defined function on the 'Page' column of the dataframe
# 2b. Using Counter, get the counts for each language

def get_language(page):
    res = re.search('[a-z][a-z].wikipedia.org',page)
    if res:
        return res[0][0:2]
    return 'na'

Melted_Wikipedia['Language'] = Melted_Wikipedia.Page.map(get_language)


print(Counter(Melted_Wikipedia.Language))

# A column for devices;
# For some of the pages in the dataset, it is possible to distinguish whether the visits to the page came from a desktop or a mobile device.
# For example, consider Barack Obama's wikipedia page:
# * Barack_Obama_en.wikipedia.org_desktop_all-agents : these visits came from desktop devices.
# * Barack_Obama_en.wikipedia.org_mobile-web_all-agents: these visits came from mobile devices.

# 3a. Define a function using re to get the name of the device used to visit a web page
# 3b. Create the new column "device"
# 3c. Count the number of searches from each device

def get_device(page):
    dev = re.search('all-access|mobile-web|desktop',page)
    if dev:
        return dev[0][0:10]
    return 'na'

Melted_Wikipedia['Device'] = Melted_Wikipedia.Page.map(get_device)


print(Counter(Melted_Wikipedia.Device))

# Drop all missing values
Melted_Wikipedia.dropna(how= 'any', inplace = True)

# Take a look at the resulting dataframe
display(Melted_Wikipedia)

# Convert the dataframe into an excel spreadsheet
# Use pd.to_excel()

Melted_Wikipedia.to_excel('Final_Wikipedia.xlsx')

# Load the data into a SQL database; sqlite3 has already been imported
# 1. Read the data from the excel spreadsheet into a pandas dataframe

Wiki_sql = pd.read_excel('Final_Wikipedia.xlsx', header=0, index_col=0)

# 2. Create a new SQLite database connection object and assign it to a variable

db_connection = sqlite3.connect("wikipedia.db")

# 3. Establish a cursor object
cursor = db_connection.cursor()

# 4. Create the database tables:
# *Run c.execute() that takes in the SQL code that creates the database table as a string


cursor.execute(
    """
    CREATE TABLE Wikipedia(
        date INTEGER,
        page TEXT NOT NULL,
        visits INTEGER,
        day TEXT NOT NULL,
        language TEXT NOT NULL,
        device TEXT NOT NULL
    );
"""
)

# 5. Populate the database

Wiki_sql.to_sql('Wikipedia',db_connection, if_exists='append', index=False)

# You can query the database using .read_sql() to see
# Use pd.read_sql to show the first 10 rows from Wikepedia

pd.read_sql('SELECT * FROM Wikipedia LIMIT 10', db_connection)