
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import pickle
import re
from dataclasses import dataclass

#get the links
def get_links(soup):
    job_soup_divs = soup.find_all('div', class_='product-details')
    job_links_list = []
    for div in job_soup_divs:
        job_links = div.find('a')['href']
        job_links_list.append(job_links)
    return job_links_list

links_list = []
category_list = ['anlagenbau','Automotive','elektrotechnik','informationstechnik',
                 'luft-und-raumfahrttechnik','maschinenbau']
for cat in category_list:
    matching_url = "https://www.matching.gmbh/produkt-kategorie/"+str(cat)
    # if page is not None
    nextPage = True
    url = matching_url #this url will be updated when there is a next page.
    while nextPage:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        # get the links in first page then proceed to the second page
        links = get_links(soup)
        links_list.extend(links)
        next_button = soup.find_all('a', class_='next page-numbers')
        if len(next_button) > 0:
            url = next_button[0]['href']
        else:
            nextPage = False

# save all downloaded links
def save_links(list):
    with open("all_links.txt", "wb") as fp1:
        pickle.dump(list,fp1)

# save all links
save_links(links_list)


# open the links
def open_links(all_links):
    with open(all_links,'rb') as fp1:
        b = pickle.load(fp1)
        return b
all_links = "all_links.txt"
links_list = open_links(all_links)

def get_title(soup):
    title_name = soup.find('h1',class_='product_title entry-title')
    title = title_name.text.strip()
    return title

def get_other_info(soup,index):
    table_category = soup.find_all('table')
    information = table_category[0].find_all('td')
    i2 = information[index].text # 0 for category, 1 job_exp, 2 city, 3 region, 4 contract
    return i2

def get_city(soup,index):
    select = soup.find_all('select')
    option = select[0].find_all('option')
    list_city = []
    for city in option:
        list_city.append(city.text)
    return list_city

# get job introduction
def get_intro_description(soup):
    content = soup.find_all('div', class_='entry-content')
    description = content[1].find('p').text
    return description

#0 if get job tasks, 1 if get candidate profile
def get_job_task(link,soup,index):
    content = soup.find_all('div', class_='entry-content')
    uls = content[1].find_all('ul')
   # print('j')
    #print(len(uls) >= 0)
    if len(uls) > 0:
        tasks = content[1].find_all('ul')[index]#.text
        return tasks
    else:
        # put these in a separate function.
        print('**Something is wrong here: ', link)
        tasks_texts = str(content[1].encode_contents())
        splitted = tasks_texts.split("<strong>Ihre Aufgaben: </strong>")
        #beschreibung = splitted[0].split("<h2>Beschreibung</h2>")[1] # already covered.
        splitted2 = splitted[1].split("<strong>Ihr Profil: </strong>")
        aufgaben = splitted2[0]
        return aufgaben


def get_profil(soup,index):
    content = soup.find_all('div', class_='entry-content')
    uls = content[1].find_all('ul')
    if len(uls) > 0:
        tasks = str(content[1].find_all('ul')[index])#.text
        return tasks
    else:
        # put these in a separate function.
        tasks_texts = str(content[1].encode_contents())
        splitted = tasks_texts.split("<strong>Ihre Aufgaben: </strong>")
        splitted2 = splitted[1].split("<strong>Ihr Profil: </strong>")
        profil = splitted2[1]
        return str(profil)


#df = pd.DataFrame({'job_title':[],'categories':[],'job_experience':[],'city':[],
 #                  'region':[],'contract_type':[],'job_intro':[],'job_task':[],'candidate_profile':[]})
data = {'job_title':[],'categories':[],'job_experience':[],'city':[],
       'region':[],'contract_type':[],'job_intro':[],'job_task':[],'candidate_profile':[]}

jobOffers = [];

for link in links_list: #(iterate here for all the links) # links_list
    print(link)
    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'html.parser')
    # get all relevant information

    try:

        jobOffer = {
                "job_title": get_title(soup),
                "categories": get_other_info(soup,0),
                "job_experience": get_other_info(soup,1),
                "city" : get_city(soup, 2),
                "region" : get_other_info(soup, 3),
                "contract_type" : get_other_info(soup, 4),
                "job_introduction" : get_intro_description(soup),
                "job_task" : str(get_job_task(link, soup, 0)),
                "candidate_profile" : get_profil(soup, 1),
              }

        jobOffers.append(jobOffer)
        #df = df.append({'job_title':job_title,
        #                'categories':categories,
        #                'job_experience':job_experience,
        #                'city':city,
        #               'region':region,
        #                'contract_type':contract_type,
        #                'job_intro':job_introduction,
        #                'job_task':job_task,
        #               'candidate_profile':candidate_profile}, ignore_index=True)


        #df.to_csv('matching_data.csv')
        #df_json = df.to_json(orient='records')

        #output_file = open('matching_rec.json', 'w')
        #json.dump(df_json, output_file)
        #output_file.close()

        #data['job_title'].append(job_title),
        #data['categories'].append(categories),
        #data['job_experience'].append(job_experience),
        #data['city'].append(city),
        #data['region'].append(region),
        #data['contract_type'].append(contract_type),
        #data['job_intro'].append(job_introduction),
        #data['job_task'].append(job_task),
        #data['candidate_profile'].append(candidate_profile)


    except Exception as e:
        print('===faulty link===' + str(e))
        print(link)

        continue
with open("C://temp/matching.json",'w')as fp1:
    json.dump(jobOffers, fp1)



def write_to_json(path, filename, data):
    fileNameExt = './'+path+ '/' + filename +'.json'
    with open(fileNameExt,'w')as fp1:
        json.dumps(str(data),fp1)


#path = './'
#filename = 'matching'
#write_to_json(path,filename,data)
























