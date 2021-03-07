from bs4 import BeautifulSoup
import urllib.parse
import requests
from os import name
from typing import Container
from lxml import html
import requests
from fake_useragent import UserAgent
import re

main_domain = "https://yummyanime.club"
http = "https:"
href = "https://yummyanime.club/catalog/item/vladyka"

class Search():

    def __init__(self) -> None:

        ua = UserAgent()
        a =ua.random
        self.headers = {"User-Agent":a }

    def find_anime(self, name_anime):

        query = {
            "q": "site:https://yummyanime.club " + name_anime,#сам запрос вместе с выражением для гугла чтобы искал только от этого сайта 
            "lr": "lang_ru",#для возврата результатов на определенном языке.
            "cr": "RU",#Для ограничения результатов поиска в определенном местоположении 
            "num": 20 #количесво ответов которое будет показано
        }

        page = requests.get("https://www.google.ru/search?" + urllib.parse.urlencode(query), headers=self.headers)

        tree = html.document_fromstring(page.text)#преобразует html в понятный для либы тип
        href =tree.xpath('//div[@class="ZINbbc xpd O9g5cc uUPGi"]//div[@class="kCrYT"]/a')#путь до поискового блока

        filter_=r"Аниме (.*?)(?:смотреть|\.\.\.)"
        filter_href =r'/url\?q=(.*?)(?:&sa=U&|%3F)'

        href_list = list()
        name_list = list()


        for item in href:
            title_block_raw = item.xpath('h3[@class="zBAuLc"]/div[@class="BNeawe vvjwJb AP7Wnd"]/text()')#получает названия всех выданых блоков
            #print(title_block)
            href_block_raw = item.get('href')

            """фильтры пустых элементов списка"""
            if title_block_raw:
                title_block = title_block_raw
            if href_block_raw:
                href_block = href_block_raw
            
            filtered_title = re.findall(str(filter_), str(title_block))#фильтрует названия блоков оставляе только предположительно сами названия аниме
            filtered_href = re.findall(str(filter_href), str(href_block))

            """фильтры пустых элементов списка"""
            if filtered_title:
                filtered_title = filtered_title
            if filtered_href:
                filtered_href = filtered_href

            if filtered_title and filtered_href:
                check = re.match(r'в жанре ', str(filtered_title[0]))
                if check == None:
                    check2 = re.match(r'от студии ', str(filtered_title[0]))
                    if check2 == None:

                        href_list.append(filtered_href[0])
                        name_list.append(filtered_title[0])
        return(name_list,href_list)  

class Anime_info():

    def __init__(self, href):
 
        """User Agent generator"""
        ua = UserAgent()
        a = ua.random
        headers = {"User-Agent": a}

        """Parsing"""
        self.page = requests.get(href, headers=headers) #получаю страницу с аниме (тут оверлорд хоть и не смотрела само аниме)

       
        if self.page.status_code != 200: #проверка доступности страницы
            print("page not found")
            quit()

        self.tree = html.document_fromstring(self.page.text)#преобразует html в понятный для либы тип

    def get_title(self):
       
        anime_title = self.tree.xpath('//div[@class="content"]/div/div[@class="content-page anime-page"]/h1/text()') #получаю сырое название с \n и подобным мусором
        anime_title = anime_title[0].strip() #получаю название (Владыка)
        return(anime_title)
    
    def get_rating(self):

        anime_rating = self.tree.xpath('//div[@class="rating-info"]//span[@class="main-rating"]/text()')
        anime_rating = anime_rating[0].strip()
        return(anime_rating)

    def get_status(self):

        anime_status = self.tree.xpath('//ul[@class="content-main-info"]/li[2]/span[2]/text()')
        anime_status = anime_status[0].strip()
        return(anime_status)

    def get_description(self):

        anime_description = self.tree.xpath('//div[@id="content-desc-text"]/p/text()')
        anime_description = anime_description[0].strip()
        return(anime_description)

    def get_players(self):
        
        dubs_list = list()
        episodes_list = list()
        video_block = self.tree.xpath(f'//div[@id="video"]//div[2]/div[@class="video-block"]')
        for item in video_block:
            data_block=item.get("data-block")
            name = self.tree.xpath(f'//div[@class="video-block"][@data-block="{data_block}"]//div[@class="video-block-description"]/text()')
            if name:
                dubs_list.append(name[0])
            episodes_l = list()
            episodes_element = self.tree.xpath(f'//div[@class="video-block"][@data-block="{data_block}"]//div[@class="video-button"]')
            for episodes in episodes_element:
                episode = episodes.get("data-href")
                episodes_l.append(episode)
            episodes_list.append(episodes_l)
        return(dubs_list,episodes_list)


class Link_extractor():

    def __init__(self):

        """User Agent generator"""
        ua = UserAgent()
        a = ua.random
        self.headers = {"User-Agent": a, "referer":main_domain}
    
    def url_detect(self,url):
        url_filter = r'//(.*?)/'
        domain = re.findall(url_filter, str(url))
        print(domain)

        if domain[0] == "kodik.info":
            link = self.kodik(url)
            return(link)

        elif domain[0] == "aniqit.com":
            link = self.kodik(url)
            link = http + link
            return(link)

        elif domain[0] =="api1571472120.delivembed.cc":
            link = self.zombi(url)
            return(link)

        elif domain[0] == "video.sibnet.ru":
            link = self.sibnet(url)
            link = http + link
            return(link)

        else:
            print("url_detect error")
            
    def kodik(self, url):

        url = http + url
        response = requests.get(url, headers=self.headers)
        print("first response: " + str(response.status_code))

        src_filter = r'src = \"(.*?)\"'
        src = re.findall(src_filter, str(response.text))
        response = requests.get("https:" + src[0], headers=self.headers)
        print("second response: " + str(response.status_code))

        VI_type = re.findall(r"videoInfo.type = \'(.*)\'", str(response.text))
        VI_hash = re.findall(r"videoInfo.hash = \'(.*)\'", str(response.text))
        VI_id = re.findall(r"videoInfo.id = \'(.*)\'", str(response.text))

        post = requests.post(f"http://kodik.info/get-video-info/?d=yummyanime.club&d_sign=8022187ea4f80a819c8b1295a86abff3713891fb8ec9f2b3958cd8152763228e&pd=kodik.info&pd_sign=09ffe86e9e452eec302620225d9848eb722efd800e15bf707195241d9b7e4b2b&ref=https%3A%2F%2Fyummyanime.club%2Fcatalog%2Fitem%2Fvladyka&ref_sign=63f2de30f0d5fe5e6d845e0d36d15414626833f2fad7aca2b5b155560e76cf5b&bad_user=false&hash2=vbWENyTwIn8I&type={VI_type[0]}&hash={VI_hash[0]}&id={VI_id[0]}&info=%7B%7D", headers=self.headers)
        print("post: " + str(post.status_code))

        data = post.json()
        links = data["links"]
        try:
            src = links["720"]
        except:
            try:
                src = links["480"]
            except:
                print("no anime links in post")

        src = src[0]["src"]
        return(src)

    def zombi(self, url):

        response = requests.get(url, headers=self.headers)
        tree = html.document_fromstring(response.text)#преобразует html в понятный для либы тип

        test = tree.xpath("/html/body/script[2]/text()")
        filter_=r'hls: \"(.*?)\"'
        link = re.findall(filter_,str(test))
        return(link[0])
    
    def sibnet(self, url):

        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, "lxml")
        raw_src = soup.find(class_="videojs_player").next_sibling
        src = re.findall(r'src: \"(.*?)\"', str(raw_src))
        path = "https://video.sibnet.ru" + src[0].strip()
        r = requests.head(path, headers={ "referer": "https://video.sibnet.ru"})
        link = r.headers["Location"]
        return(link)




name_anime ="Overlord"
search = Search()
search_titles, search_links = search.find_anime(name_anime)

num = 1


anime = Anime_info(search_links[0])
print("name: " + anime.get_title()) 
print("rating: " + anime.get_rating())
print("status: " + anime.get_status())
print("description: " + anime.get_description())
dubs, episodes = anime.get_players()
if num > len(dubs):
    print("out from range")
    quit()
print("dub: " + dubs[num])
print(episodes[num][0])
extractor = Link_extractor()
print("link: " + extractor.url_detect(episodes[num][0]))