#!/usr/bin/env python
#SI 330 Final Project Viviana Hernandez

import csv
from urllib.request import urlopen
import urllib
from bs4 import BeautifulSoup
import re


def step1_fetch_election():
    # 1. Get response
    response = urllib.request.urlopen("http://www.infoplease.com/us/government/2012-presidential-election-vote-summary.html")
    #http://elections.nytimes.com/2012/results/president/big-board

    # 2. Read response html into html variable
    html = response.read().decode("utf-8")

    # 3. Write response html into step1.html
    with open('step1.html', 'w') as outfile:
       outfile.write(html)

def step2_extract_electiondata():
    # 1. Read step1.html
    with open('step1.html', 'r') as infile:
        html = infile.read()

    # 2. Parse using BeautifulSoup
    # If you get a warning, use: BeautifulSoup(YOUR_HTML_VARIABLE, "html.parser")
    soup = BeautifulSoup(html,"html.parser")
    #print(soup.prettify())


    # 3. Find all table
    table = soup.find_all("table")[1]
    # print(table)
    rows= table.find_all("tr")
    # print(rows)

    #4. Loop through each  row,
    #use beautiful soup function and/or regular expressions
    state_dict2 ={}
    for row in rows:
        columns=row.find_all("td")
        if len(columns) == 0:
            continue
        state= columns[0].text
        obama_vote_percent = columns[2].text
        romney_vote_percent = columns[4].text
        # print(rows)
        # print(state)
        # print(obama_vote_percent)
        # print(romney_vote_percent)

        state_dict2[state.lower()]= (obama_vote_percent,romney_vote_percent)
    return(state_dict2)

# read the census file
def read_medianincome_file(filename):
   median_income = dict()  # create an empty dictionary
   with open(filename, 'r', newline='') as input_file:
       region_reader = csv.DictReader(input_file, delimiter=',', quotechar ='"')
       for row in region_reader:
           median_income[row["Name"].lower()] = row["Median Household Income"]
           #create a dictionary that contains the name of the state as the key
           # make the median household income for that state value
   return median_income



def main():

    step1_fetch_election() # will return the html for the election data that needs to be scraped
    election_datadict=step2_extract_electiondata() # the function creates a dictionary of tuples
    state_income = read_medianincome_file('est12US.csv') #this makes the median_income dictionary returned
    #from the function equal to state income

    #print(state_income)


    #open the input csv data file
    with open('table_5_crimerate_2012.csv') as input_file:
        # table_5_crime_in_the_united_states_by_state_2012 is the original csv
        # the one here is modified due to issues to converting it to a txt or csv file
        # prepare to read the rows of the file using the csv package DictReader
        crime_stats_reader = csv.DictReader(input_file)

        #open a new output file to store your new data
        with open('crime_politics_output.csv', 'w', newline='') as output_file:
            #prepare to write out rows to the output file we are using/ a new subset
            crime_stats_writer = csv.DictWriter(output_file, fieldnames= ['STATE','VIOLENT CRIMES','PROPERTY CRIMES','Democrat',"Republican","Party Choice","Median HouseHold Income", "Violent Crimes Democrat", "Violent Crimes Republican","Property Crimes Democrat","Property Crimes Republican","Scaled Median HouseHold Income"],
                                                 extrasaction = 'ignore',
                                                 delimiter = ',', quotechar = '"')

            #write the column header to the output file
            crime_stats_writer.writeheader()
            row_count = 0

            for row in crime_stats_reader:
                row['STATE'] = re.sub(r"[0-9]","",row["State"]).lower() #some states had digits in them
                # needed to make all the states lower case so I could use the same key for the dictionaries created
                row['VIOLENT CRIMES'] = row["Violent crime"]
                row['PROPERTY CRIMES']= row["Property crime"]

                if row["STATE"] not in election_datadict: #the fbi had states that weren't necessarily states i.e. Puerto Rico
                    continue
                row['Democrat']= (election_datadict[row["STATE"]][0]).rstrip("%") # some numbers had percentages on them
                row["Republican"]= (election_datadict[row["STATE"]][1]).rstrip("%") #needed to index what part of the dict
                # i needed to make sure I go the right number for each state.

                #coding if the state voted  democrat and republican
                if row['Democrat'] > row['Republican'] :  # if the demo number is larger than the rep then
                    row['Party Choice'] = 1 #democrat
                else:
                    row['Party Choice']= 0 #republican
                # to solve visualization issues
                #basically splitting up violent crimes into democrat or republican
                #coding the violent crimes rep/dem
                if row["Party Choice"] == 1:
                    row["Violent Crimes Democrat"] = row["VIOLENT CRIMES"]
                else:
                    row["Violent Crimes Republican"] = row["VIOLENT CRIMES"]

                #to solve visualization issues
                # coding the property crimes rep/dem
                if row["Party Choice"] == 1:
                    row["Property Crimes Democrat"] = row["PROPERTY CRIMES"]
                else:
                    row["Property Crimes Republican"] = row["PROPERTY CRIMES"]

                #added the row median household income to my output
                #used a regular expression to get rid of the extra commas
                # used states from my output csv as a key to my dictionary
                row['Median HouseHold Income'] = re.sub(r"[^0-9]", "", state_income[row["STATE"]])
                # scaling the median household income so it'll look cooler on the map (:
                row["Scaled Median HouseHold Income"] = float(row["Median HouseHold Income"]) - 37179 + 1
                #keeps track of the rows
                row_count = row_count + 1
                crime_stats_writer.writerow(row) # write the rows to the csv i am out putting. 

if __name__ == '__main__':
    main()