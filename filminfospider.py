import requests
import time
import random
import re
import json
import bs4

head = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}

find_name = re.compile(r'<h1.*?>(.*?)</h1>')
find_year = re.compile(r'<p class="db_year".*?>\(<a.*?>(\d.*?)</a>\)')
find_enname = re.compile(r'<p class="db_enname".*?>(.*?)</p>')

find_img = re.compile(r'<img.*?src="(.*?)"/></a>')

find_url = re.compile(r'<a href="(.*?)">')

find_plot = re.compile(r'<p>\s*<span class="first_letter">(.*?)</span>(.*?)</p>')

find_ppl_id = re.compile(r'<h3><a href="http://people.mtime.com/(\d*)/"')

find_comment = re.compile(r'<div.*?tweetid=.*?\n?<h3>(.*?)</h3>')

find_ppl_name = re.compile(r'<h2.*?>(.*?)</h2>')
find_ppl_enname = re.compile(r'<p class="enname".*?>(.*?)</p>')

find_photo = re.compile(r'<img.*?src="(.*?)".*?>')


def main():
    file = open("urls.txt", mode='r')
    film_list = []
    ppl_list = []
    lines = file.readlines()
    film_count = 0
    for url in lines[:1000]:
        film_count = film_count + 1
        print("requesting film " + str(film_count) + " at " + url)

        film_id = re.sub('\D', '', url)

        doc_response = requests.get(url, headers=head).text
        doc_soup = bs4.BeautifulSoup(doc_response, "html.parser")
        name_info = doc_soup.find('div', {"pan": "M14_Movie_Overview_Name"})  # 找name组件
        name_info = str(name_info)

        film_name = ""
        result = re.findall(find_name, name_info)
        if result:
            film_name = result[0]

        film_year = ""
        result = re.findall(find_year, name_info)
        if result:
            film_year = result[0]

        film_enname = ""
        result = re.findall(find_enname, name_info)
        if result:
            film_enname = result[0]
        # print(film_name)
        # print(film_year)
        # print(film_enname)

        cover_info = doc_soup.find('div', {"pan": "M14_Movie_Overview_Cover"})  # 找cover组件
        cover_info = str(cover_info)

        film_poster = ""
        result = re.findall(find_img, cover_info)
        if result:
            film_poster = result[0]
        # print(film_poster)

        plot_info = doc_soup.find('dt', {"pan": "M14_Movie_Overview_PlotsSummary"})  # 找plotssummary组件
        plot_info = str(plot_info)

        plot_url = "http://movie.mtime.com/" + str(film_id) + "/plots.html"
        plot_response = requests.get(plot_url, headers=head).text
        plot_soup = bs4.BeautifulSoup(plot_response, "html.parser")
        plot_sum = plot_soup.find('div', class_="plots_box")  # 找第一个plot box
        plot_sum = str(plot_sum)
        result = re.findall(find_plot, plot_sum)
        if result:
            film_plot = result[0]
            film_plot = film_plot[0] + film_plot[1]
            film_plot = re.sub('<.*?>', r'', film_plot)
        # print(film_plot)

        more_actor = doc_soup.find('p', {"pan": "M14_Movie_Overview_Actor_More"})  # 找更多演员
        more_actor = str(more_actor)

        actor_ids = []
        result = re.findall(find_url, more_actor)
        if result:
            cast_url = result[0]
            cast_response = requests.get(cast_url, headers=head).text
            cast_soup = bs4.BeautifulSoup(cast_response, "html.parser")
            actor_info = cast_soup.find_all('div', class_="db_actor")
            actor_info = str(actor_info)
            actor_ids_all = re.findall(find_ppl_id, actor_info)
            actor_ids = actor_ids_all[:10]
        # print(actor_ids)

        comment_area = doc_soup.find_all('dl', {"pan": "M14_Movie_Overview_ShortReview_List"})
        comment_area = str(comment_area)
        short_comments_all = re.findall(find_comment, comment_area)
        short_comments = short_comments_all[:5]
        # print(short_comments)

        # 写入film_list
        film_dic = {"id": film_id,
                    "name": film_name,
                    "enname": film_enname,
                    "year": film_year,
                    "poster": film_poster,
                    "actors": actor_ids,
                    "plot": film_plot,
                    "comments": short_comments}
        film_list.append(film_dic)

        # 用actor_ids抓取actor，并每次判断是否已有此人，有则跳过

        for id in actor_ids:  # 记得改回去
            flag = False
            for actor in ppl_list:
                if actor["id"] == id:
                    flag = True
                    break
            if flag:
                continue  # 跳过已经有的人
            ppl_url = "http://people.mtime.com/" + str(id) + "/"
            ppl_response = requests.get(ppl_url, headers=head).text
            ppl_soup = bs4.BeautifulSoup(ppl_response, "html.parser")
            ppl_info = ppl_soup.find('div', class_="per_header")  # 找人头
            ppl_info = str(ppl_info)
            ppl_name = ""
            ppl_enname = ""
            result = re.findall(find_ppl_name, ppl_info)
            if result:
                ppl_name = result[0]
            result = re.findall(find_ppl_enname, ppl_info)
            if result:
                ppl_enname = result[0]
            # print(ppl_name)
            # print(ppl_enname)
            photo_info = ppl_soup.find_all('div', {"pan": "M14_Person_Index_PersonCover"})  # 找照片
            photo_info = str(photo_info)

            ppl_photo = ""
            result = re.findall(find_photo, photo_info)
            if result:
                ppl_photo = result[0]
            # print(ppl_photo)

            detail_url = ppl_url + "details.html"
            detail_response = requests.get(detail_url, headers=head).text
            detail_soup = bs4.BeautifulSoup(detail_response, "html.parser")
            graphy_info = detail_soup.find('div', {"id": "lblAllGraphy"})
            graphy_info = str(graphy_info)
            graphy_info = re.sub('<.*?>', r'', graphy_info)  # 去除html脚本部分
            ppl_graphy = str(graphy_info)
            # print(ppl_graphy)

            # 写入ppl_list
            ppl_dic = {"id": id,
                       "name": ppl_name,
                       "enname": ppl_enname,
                       "photo": ppl_photo,
                       "graphy": ppl_graphy}
            ppl_list.append(ppl_dic)

        time.sleep(random.random())

    # print(film_list)
    # print(ppl_list)
    with open('filmlist.json', 'w', encoding="utf-8") as file:
        file.write(json.dumps(film_list, indent=2, ensure_ascii=False))
    with open('ppllist.json', 'w', encoding="utf-8") as file:
        file.write(json.dumps(ppl_list, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
