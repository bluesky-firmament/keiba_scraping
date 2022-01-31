import csv
import urllib.request
from bs4 import BeautifulSoup
def main():
    for number in range(1,1000):
        # url = "https://db.netkeiba.com/horse/2017101835"
        url = "https://db.netkeiba.com/horse/201710"
        url = url + str("{:0>4}".format(number))
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
            if table_className[0] == "db_h_race_results":
                break
        # print("ファイル名を打ち込んでください")
        # name = input()
        csvname = "horse_result_data/" + horse_name + ".csv"
        for tab in table:
            table_className = tab.get("class")
            if table_className[0] == "db_h_race_results":
                with open(csvname, "w", encoding='utf-8',newline="") as file:
                    writer = csv.writer(file)
                    rows = tab.find_all("tr")
                    for row in rows:   
                        csvRow = []
                        for cell in row.findAll(['td', 'th']):
                            try:
                                # element = str(cell.contents[0])
                                # csvRow.append(element.replace('/',','))
                                csvRow.append(cell.get_text())
                            except IndexError:
                                continue
                        # integration = ','.join(csvRow)
                        # degration = integration.split(',')
                        # writer.writerow(degration)
                        writer.writerow(csvRow)
                break

if __name__ == "__main__":
    main()