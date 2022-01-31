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
        print(horse_name)
        table = soup.find_all("table")
        for tab in table:
            print(tab.get("class"))
            table_className = tab.get("class")
            if table_className[0] == "blood_table":
                break
        # print("ファイル名を打ち込んでください")
        # name = input()
        horse_line = np.empty((1024,10),dtype='U20')
        position_x=0
        position_y=0
        csvname = "horse_blood_data/" + horse_name + ".csv"
        for tab in table:
            table_className = tab.get("class")
            if table_className[0] == "blood_table":
                with open(csvname, "w", encoding='utf-8',newline="") as file:
                    writer = csv.writer(file)
                    rows = tab.find_all("tr")
                    for row in rows:   
                        Row = []
                        for cell in row.findAll(['td', 'th']):
                            try:
                                # element = str(cell.contents[0])
                                # csvRow.append(element.replace('/',','))
                                newline_number = cell.get_text().find("\n",1)
                                parent_horse_name = cell.get_text()[1:newline_number]
                                horse_line[position_y*32][position_x] = parent_horse_name
                                position_x = position_x + 1
                                print(parent_horse_name)
                                Row.append(parent_horse_name)
                            except IndexError:
                                continue
                        
                        position_y = position_y + 1
                        print(len(Row))
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
                        # position_x = position_x - len(csvRow)
                        
                        for iteration in range(0,5 - len(Row)):
                            Row.insert(0,"")
                        # integration = ','.join(csvRow)
                        # degration = integration.split(',')
                        # writer.writerow(degration)
                        # writer.writerow(csvRow)
                break
        print(horse_line)
        pd.DataFrame(horse_line).to_csv(csvname,header=False, index=False)

def add_horse_line(individual_url,horse_matrix,position):
    html = urllib.request.urlopen(url)
    soup = BeautifulSoup(html, 'html.parser')
    name = soup.find_all('h1')
    horse_name = str(name[1])
    # print(type(horse_name))
    horse_name = horse_name.replace(" ","").replace("　","").replace("<h1>","").replace("</h1>","")
    print(horse_name)
    table = soup.find_all("table")
    for tab in table:
        print(tab.get("class"))
        table_className = tab.get("class")
        if table_className[0] == "blood_table":
            break
    print("test")

if __name__ == "__main__":
    # print(np.empty((1024,10),dtype=np.unicode))
    main()