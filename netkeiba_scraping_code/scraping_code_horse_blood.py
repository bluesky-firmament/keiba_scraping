import csv
from multiprocessing.connection import wait
from urllib.parse import urlencode
import time
import urllib.request
import numpy as np
import pandas as pd
import os
from bs4 import BeautifulSoup
def main():
    url = "https://db.netkeiba.com/horse/ped/2017101835"
    # race_url = "https://race.netkeiba.com/race/shutuba.html?race_id=202109010101"
    race_base_url = "https://race.netkeiba.com/race/shutuba.html?race_id="
    year = 2021
    horse_list = []
    horse_list_csv = "horse_list.csv"
    for circuit in range(1,11):
        for number_iteration in range(1,6):
            for days in range(1,13):
                for races in range(1,12):
                    race_url = race_base_url + str(f'{year:0}') + str(f'{circuit:02}') + str(f'{number_iteration:02}') + str(f'{days:02}') + str(f'{races:02}')
                    # print(race_url)
                    get_race_list(horse_list,race_url)
                    # print(horse_list)
                    if(horse_list == []):
                        continue
    
    np.savetxt(horse_list_csv, horse_list, delimiter =",",fmt ='% s')
    # horse_list = []
    # horse_list = np.loadtxt(horse_list_csv, delimiter =",", dtype='str')
    # print(horse_list[0])
    # for individual_horse_url in horse_list:
        # horse_one_step(individual_horse_url)

def horse_one_step(url):
    print(url)
    horse_name,soup = url_parser(url)

    horse_line = np.empty((1024,10),dtype='U20')
    blood_data_folder = "horse_blood_data/"
    blood_value_folder = "horse_blood_value_data/"
    os.makedirs(blood_data_folder, exist_ok=True)
    os.makedirs(blood_value_folder, exist_ok=True)
    csvname = blood_data_folder + horse_name + ".csv"
    blood_value_csvname = blood_value_folder + horse_name + ".csv"
    oldhorse_url_list = [] 
    position_x = 0
    position_y = 0

    # 血量テスト
    blood_percentage = []
    
    initial_horse_line(url,horse_line,position_x,position_y,oldhorse_url_list,blood_percentage)
    iteration = 0
    time.sleep(0.5)
    for several_url in oldhorse_url_list:
        add_horse_line(several_url,horse_line,5,32*iteration,blood_percentage)
        iteration = iteration + 1
        time.sleep(0.1)
    pd.DataFrame(horse_line).to_csv(csvname,header=False, index=False)
    df = pd.json_normalize(blood_percentage)
    df.to_csv(blood_value_csvname, index=False, encoding='utf-8', quoting=csv.QUOTE_ALL)

def initial_horse_line(individual_url,horse_line,position_x,position_y,oldhorse_url_list,blood_percentage):
    horse_name,soup = url_parser(individual_url)
    table = soup.find_all("table")
    for tab in table:
        table_className = tab.get("class")
        if table_className[0] == "blood_table":
            rows = tab.find_all("tr")
            for row in rows:   
                Row = []
                for cell in row.findAll(['td', 'th']):
                    try:
                        newline_number = cell.get_text().find("\n",1)
                        parent_horse_name = cell.get_text()[1:newline_number]
                        horse_line[position_y*32][position_x] = parent_horse_name
                        position_x = position_x + 1
                        blood_percentage_dict ={}
                        blood_append_flag = 0
                        for i in range (0,len(blood_percentage)):
                            if(blood_percentage[i]["horse_name"] == parent_horse_name):
                                blood_percentage_tmp = blood_percentage[i]["percentage"] + 1 / pow(2,(position_x))
                                blood_percentage[i]["percentage"] = blood_percentage_tmp
                                blood_append_flag = 1
                                break
                        blood_percentage_dict["horse_name"] = parent_horse_name
                        blood_percentage_dict.setdefault("percentage",1.0 / pow(2,(position_x)))
                        if(blood_append_flag == 0):
                            blood_percentage.append(blood_percentage_dict)
                        # print(parent_horse_name)
                        Row.append(parent_horse_name)
                        if(position_x == 5):
                            horse_url = soup.find_all('a')
                            for individual_horse_url in horse_url:
                                if(parent_horse_name in str(individual_horse_url)):
                                    individual_url = individual_horse_url.get('href')
                                    individual_url_header = individual_url[:7] + "ped/"
                                    individual_url_footter = individual_url[7:]
                                    oldhorse_url_list.append("https://db.netkeiba.com" + individual_url_header + individual_url_footter)
                    except IndexError:
                        continue
                
                position_y = position_y + 1
                if((position_y % 16 == 0)):
                    position_x = 0
                elif((position_y % 8 == 0)):
                    position_x = 1
                elif((position_y % 4 == 0)):
                    position_x = 2
                elif((position_y % 2 == 0)):
                    position_x = 3
                else:
                    position_x = 4
        break

def add_horse_line(individual_url,horse_matrix,position_x,position_y,blood_percentage):
    horse_name,soup = url_parser(individual_url)
    table = soup.find_all("table")
    for tab in table:
        table_className = tab.get("class")
        if table_className[0] == "blood_table":
            rows = tab.find_all("tr")
            for row in rows:   
                Row = []
                for cell in row.findAll(['td', 'th']):
                    try:
                        newline_number = cell.get_text().find("\n",1)
                        parent_horse_name = cell.get_text()[1:newline_number]
                        horse_matrix[position_y][position_x] = parent_horse_name
                        position_x = position_x + 1
                        blood_percentage_dict ={}
                        blood_append_flag = 0
                        for i in range (0,len(blood_percentage)):
                            if(blood_percentage[i]["horse_name"] == parent_horse_name):
                                blood_percentage_tmp = blood_percentage[i]["percentage"] + 1 / pow(2,(position_x))
                                blood_percentage[i]["percentage"] = blood_percentage_tmp
                                blood_append_flag = 1
                                break
                        blood_percentage_dict["horse_name"] = parent_horse_name
                        blood_percentage_dict.setdefault("percentage",1 / pow(2,(position_x)))
                        if(blood_append_flag == 0):
                            blood_percentage.append(blood_percentage_dict)
                        Row.append(parent_horse_name)
                    except IndexError:
                        continue
                position_y = position_y + 1
                if((position_y % 16 == 0)):
                    position_x = 5
                elif((position_y % 8 == 0)):
                    position_x = 6
                elif((position_y % 4 == 0)):
                    position_x = 7
                elif((position_y % 2 == 0)):
                    position_x = 8
                else:
                    position_x = 9
            break

def url_parser(url):
    html = urllib.request.urlopen(url)
    soup = BeautifulSoup(html, 'html.parser')
    name = soup.find_all('h1')
    try:
        horse_name = str(name[1])
    except IndexError:
        horse_name = ""
    horse_name = horse_name.replace(" ","").replace("　","").replace("<h1>","").replace("</h1>","")
    return horse_name,soup

def get_race_list(horse_list,race_url):
    html = urllib.request.urlopen(race_url)
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find("a")
    for tab in table:
        for tab2 in soup.find_all('span',class_='HorseName'):
            # horse_url = tab2.find_all('a')
            # print(tab2)
            for tab3 in tab2:
                try:
                    individual_url = tab3.get('href')
                    individual_url_header = individual_url[:30] + "ped/"
                    individual_url_footter = individual_url[30:]
                    horse_list.append(individual_url_header + individual_url_footter)
                except AttributeError:
                    continue
        break

if __name__ == "__main__":
    main()