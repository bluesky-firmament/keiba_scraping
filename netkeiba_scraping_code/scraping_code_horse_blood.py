import csv
from turtle import pos, position
import urllib.request
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
def main():
    for number in range(1,2):
        # url = "https://db.netkeiba.com/horse/201710"
        url = "https://db.netkeiba.com/horse/ped/2017101835"
        # url = url + str("{:0>4}".format(number))
        print(url)
        # print("URLを入れてください")
        # url = input()
        html = urllib.request.urlopen(url)
        soup = BeautifulSoup(html, 'html.parser')
        name = soup.find_all('h1')
        horse_name = str(name[1])
        # print(type(horse_name))
        horse_name = horse_name.replace(" ","").replace("　","").replace("<h1>","").replace("</h1>","")
        horse_line = np.empty((1024,10),dtype='U20')
        csvname = "horse_blood_data/" + horse_name + ".csv"
        oldhorse_url_list = [] 
        position_x = 0
        position_y = 0
        blood_percentage = {}
        initial_horse_line(url,horse_line,position_x,position_y,oldhorse_url_list,blood_percentage)
        iteration = 0
        for several_url in oldhorse_url_list:
            add_horse_line(several_url,horse_line,5,32*iteration,blood_percentage)
            iteration = iteration + 1
        pd.DataFrame(horse_line).to_csv(csvname,header=False, index=False)
        df = pd.json_normalize(blood_percentage)
        df.to_csv(csvname, index=False, encoding='utf-8', quoting=csv.QUOTE_ALL)

def initial_horse_line(individual_url,horse_line,position_x,position_y,oldhorse_url_list,blood_percentage):
    html = urllib.request.urlopen(individual_url)
    soup = BeautifulSoup(html, 'html.parser')
    name = soup.find_all('h1')
    horse_name = str(name[1])
    table = soup.find_all("table")
    for tab in table:
        table_className = tab.get("class")
        if table_className[0] == "blood_table":
            break
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
                        try:
                            if(blood_percentage[parent_horse_name] != 0.0):
                                blood_percentage[parent_horse_name] = blood_percentage[parent_horse_name] + 1.0 / pow(2,(position_x))
                        except KeyError:
                            blood_percentage[parent_horse_name] = 1.0 / pow(2,(position_x))
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
    html = urllib.request.urlopen(individual_url)
    soup = BeautifulSoup(html, 'html.parser')
    name = soup.find_all('h1')
    horse_name = str(name[1])
    table = soup.find_all("table")
    for tab in table:
        table_className = tab.get("class")
        if table_className[0] == "blood_table":
            break
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
                        try:
                            if(blood_percentage[parent_horse_name] != 0.0):
                                blood_percentage[parent_horse_name] = blood_percentage[parent_horse_name] + 1.0 / pow(2,(position_x))
                        except KeyError:
                            blood_percentage[parent_horse_name] = 1.0 / pow(2,(position_x))
                        # print(parent_horse_name)
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

if __name__ == "__main__":
    main()