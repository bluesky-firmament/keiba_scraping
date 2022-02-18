import csv
from multiprocessing.connection import wait
from unittest import result
from urllib.parse import urlencode
import time
import urllib.request
import numpy as np
import pandas as pd
import os
from bs4 import BeautifulSoup
def main():
    year = 2021
    horse_blood_list = []
    horse_blood_list_csv = "horse_blood_list.csv"
    horse_result_list = []
    horse_result_list_csv = "horse_result_list.csv"
    race_url = "https://race.netkeiba.com/race/shutuba.html?race_id=202205010711"
    # add_racelist_to_horselist(horse_blood_list,horse_result_list,year)
    get_race_list(horse_blood_list,horse_result_list,race_url)
    # print(horse_blood_list)
    np.savetxt(horse_blood_list_csv, horse_blood_list, delimiter =",",fmt ='% s')
    np.savetxt(horse_result_list_csv, horse_result_list, delimiter =",",fmt ='% s')
    
    horse_blood_list = []
    horse_blood_list = np.loadtxt(horse_blood_list_csv, delimiter =",", dtype='str')
    horse_result_list = []
    horse_result_list = np.loadtxt(horse_result_list_csv, delimiter =",", dtype='str')

    for individual_horse_url in horse_blood_list:
        horse_one_step_blood(individual_horse_url)
    for individual_horse_url in horse_result_list:
        horse_one_step_result(individual_horse_url)

def horse_one_step_blood(url):
    print(url)
    horse_name,soup = url_parser(url)

    horse_line = np.empty((1024,10),dtype='U20')
    blood_data_folder = "horse_blood_data/"
    blood_value_folder = "horse_blood_value_data/"
    os.makedirs(blood_data_folder, exist_ok=True)
    os.makedirs(blood_value_folder, exist_ok=True)
    csvname = blood_data_folder + horse_name + ".csv"
    csvname_md = blood_data_folder + horse_name + ".md"
    if(os.path.exists(csvname)):
        print("this file is exist")
        return
    blood_value_csvname = blood_value_folder + horse_name + ".csv"
    blood_value_csvname_md = blood_value_folder + horse_name + ".md"
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
    df.to_csv(blood_value_csvname_md, index=False, encoding='utf-8', quoting=csv.QUOTE_ALL)

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
    horse_name = horse_name.replace(" ","").replace("　","").replace("<h1>","").replace("</h1>","").replace("□地","").replace("○地","").replace("□外","").replace("○外","")
    return horse_name,soup

def get_race_list(horse_blood_list,horse_result_list,race_url):
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
                    individual_blood_url_header = individual_url[:30] + "ped/"
                    individual_blood_url_footter = individual_url[30:]
                    horse_result_list.append(individual_url)
                    horse_blood_list.append(individual_blood_url_header + individual_blood_url_footter)
                except AttributeError:
                    continue
        break

def add_racelist_to_horselist(horse_list,result_list,year):
    race_base_url = "https://race.netkeiba.com/race/shutuba.html?race_id="
    for circuit in range(1,2):
        # 1:札幌 2:函館 3:福島 4:新潟 5:東京 6:中山 7:中京 8:京都 9:阪神 10:小倉
        for number_iteration in range(1,6):
            for days in range(1,13):
                for races in range(10,13):
                    race_url = race_base_url + str(f'{year:0}') + str(f'{circuit:02}') + str(f'{number_iteration:02}') + str(f'{days:02}') + str(f'{races:02}')
                    # print(race_url)
                    get_race_list(horse_list,result_list,race_url)
                    # print(horse_list)
                    if(horse_list == []):
                        continue

def horse_one_step_result(url):
    horse_name,soup = url_parser(url)
    table = soup.find_all("table")
    race_data_folder = "horse_race_data/"
    property_folder = "horse_property_data/"
    
    os.makedirs(race_data_folder, exist_ok=True)
    os.makedirs(property_folder, exist_ok=True)
    race_data_csvname = race_data_folder + horse_name + ".csv"
    property_data_csvname = property_folder + horse_name + ".csv"
    if(os.path.exists(race_data_csvname)):
        print("this file is exist")
        return
    get_race_data(table,race_data_csvname)
    get_property_data(table,property_data_csvname)
    time.sleep(0.1)

def get_race_data(table,race_data_csvname):
    for tab in table:
        table_className = tab.get("class")
        if table_className[0] == "db_h_race_results":
            with open(race_data_csvname, "w", encoding='utf-8',newline="") as file:
                writer = csv.writer(file)
                rows = tab.find_all("tr")
                for row in rows:   
                    csvRow = []
                    for cell in row.findAll(['td', 'th']):
                        try:
                            add_text = cell.get_text()
                            add_text = add_text.replace('\n','')
                            csvRow.append(add_text)
                        except IndexError:
                            continue
                    # integration = ','.join(csvRow)
                    # degration = integration.split(',')
                    # writer.writerow(degration)
                    writer.writerow(csvRow)
            break

def get_property_data(table,property_data_csvname):
    horse_result = ""
    flag = 0
    for tab in table:
        table_className = tab.get("class")
        if table_className[0] == "db_prof_table":
            with open(property_data_csvname, "w", encoding='utf-8',newline="") as file:
                writer = csv.writer(file)
                rows = tab.find_all("tr")
                for row in rows:   
                    csvRow = []
                    for cell in row.findAll(['td', 'th']):
                        try:
                            add_text = cell.get_text()
                            add_text = add_text.replace('\n','')
                            csvRow.append(add_text)
                        except IndexError:
                            continue
                    # integration = ','.join(csvRow)
                    # degration = integration.split(',')
                    # writer.writerow(degration)
                    writer.writerow(csvRow)
            break
    

if __name__ == "__main__":
    main()