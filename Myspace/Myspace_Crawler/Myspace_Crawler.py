# Inspired By Cr1tika7's myspace crawler, go check it out! http://www.lostwave-tools.cr1tika7.com/myspace/song_crawler

import requests
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from math import floor
from json import loads, dumps
from time import sleep
from os import makedirs
from re import sub

query = "we were kings" # search query

Max_Retry = 10 # max retries before skipping the page

jsonToggle = True # if you want a json file, better for filtering with like scripts and stuff :3

Setup = True # set to False to turn off that initial setup

# Myspace is kool so you don't need an api key or anything!! waow!!

class mySpace:
    def __init__(self, query : str, session : requests.Session, cookies : str) -> None:
        try:
            self.query = query
            self.session = session
            self.cookies = cookies
            self.hash = None
            self.ssid = None

            if session is None or cookies is None:
                raise KeyError("session or cookies are missing :P")
        except KeyError as e:
            print("KeyError: {e}")
        except TypeError as e:
            print(f"TypeError{e}")
        except Exception as e:
            print(f"Unknown Error: {e}")
    def returnPages(self) -> int:
        def returnSongCount():
            baseUrl = "https://myspace.com/ajax/search/autocomplete/?"
            encoded = urlencode({"q" : self.query, "limit" : 20})
            url = f"{baseUrl}{encoded}"
            headers = {
                "Hash" : self.hash, 
                "Content-Type" : "application/x-www-form-urlencoded; charset=UTF-8",
                "Accept" : "*/*",
                "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
            }
            response = self.session.post(url=url, data={"searchType" : "songs", "ssid" : self.ssid}, cookies=self.cookies, headers=headers)

            if response.status_code == 200:
                pageJson = loads(response.text)
                total = (pageJson.get("total", 0))
                return total
            else:
                print(f"Couldn't get pages: Code {response.status_code}")
        # songs / 20
        songCount = returnSongCount()
        pageCount = floor(songCount / 20)
        return pageCount
    def returnSongs(self, Page: int):
        debounce = False
        localRetryRate = Max_Retry
        currentRate = 1
        while not debounce:
            def htmlToJson(html: str):
                def oneSong(songHtml):
                    songTable = []
                    def extract_text(soup, class_name):
                            element = soup.find("div", {"class": class_name})
                            return element.text.strip() if element else ""
                    for soup in songHtml:
                        artist = extract_text(soup, "artist")
                        album = extract_text(soup, "album")
                        date = extract_text(soup, "date")
                        title = extract_text(soup, "title")
                        duration = extract_text(soup, "duration")

                        song = {
                            "title": title,
                            "album": album,
                            "artist": artist,
                            "date": date,
                            "duration": duration
                        }


                        songTable.append(song)
                    return songTable
                    
                soup = BeautifulSoup(html, "html.parser")

                newSongTable = soup.find_all("div", {"class" : "flex"})
                songTable = oneSong(newSongTable)

                return songTable


            base = "https://myspace.com/ajax/page/search/"
            encoded = urlencode({'q' : self.query})
            url = f"{base}songs?{encoded}"
            headers = {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
                "Accept" : "*/*",
                "Hash" : self.hash
            }
            data = {
                "page" : Page,
                "ssid" : self.ssid
            }
            response = self.session.post(url=url, cookies=self.cookies, headers=headers, data=data)
            
            if response.status_code == 200:
                songTable = htmlToJson(response.text)
                debounce = True
                return songTable
            elif response.status_code == 500:
                if currentRate > Max_Retry:
                    return None
                print(f"Retrying {currentRate} out of {Max_Retry}")
                sleep(3)
                currentRate += 1
            
    def get_SSID(self):
        def returnHash(html) -> str:
            try:
                soup = BeautifulSoup(html, "html.parser")

                inputHtml = soup.find("input", {"name" : "csrf"})
                hash = inputHtml.get("value", None)

                if hash is None:
                    raise KeyError("Hash not found")
                return hash
            except KeyError as e:
                print(f"KeyError: {e}")
            except TypeError as e:
                print(f"TypeError: {e}") 
            except Exception as e:
                print(f"Unknown Error Returning Hash: {e}")
        def returnSSID(html):
            try:
                soup = BeautifulSoup(html, "html.parser")

                inputHtml = soup.find("input", {"data-tour-id" : "searchinput"})
                hash = inputHtml.get("data-ssid", None)

                if hash is None:
                    raise KeyError("SSID not found")
                return hash
            except KeyError as e:
                print(f"KeyError: {e}")
            except TypeError as e:
                print(f"TypeError: {e}") 
            except Exception as e:
                print(f"Unknown Error Returning Hash: {e}")


        baseURL = "http://myspace.com/search/"
        encoded = urlencode({"q" : self.query})
        url = f"{baseURL}songs?{encoded}"
        response = self.session.get(url=url, cookies=self.cookies)
        if response.status_code == 200:
            hashCode = returnHash(response.text)
            ssid = returnSSID(response.text)
            self.hash = hashCode
            self.ssid = ssid
            return hashCode
        else:
            print("Error Getting Hash")
    def mainCrawler(self):
        pages = self.returnPages()
        songTable = []
        for i in range(0, pages+1):
            print(f"Crawling page {str(i+1)} out of {str(pages+1)}")
            page = self.returnSongs(Page=i+1)
            if page is not None:
                songTable.append(page)
        return songTable
    
    def finishAndFormatJson(self, json):
        def blerpbleepbloop(fileName : str):
            return sub(r'[<>:"/\\|?*]', '', fileName)
    
        makedirs("Results", exist_ok=True)
        safeFileName = blerpbleepbloop(self.query)
        if jsonToggle == False:
            with open(f"Results/{safeFileName}.txt", "a", encoding="utf-8") as f:
                for songGroup in json:
                    for singleSong in songGroup:
                        try:
                            formatted = f'Title: {singleSong["title"]}, Artist: {singleSong["artist"]}, Album: {singleSong["album"]}, Date: {singleSong["date"]}, duration: {singleSong["duration"]}\n\n'
                            f.write(formatted)
                        except Exception as e:
                            print(f"Failed to input a song for some reason idk: {e}")
        else:
            formattedjson = []
            with open(f"Results/{safeFileName}.json", "a", encoding="utf-8") as f:
                for songGroup in json:
                    for singleSong in songGroup:
                        try:
                            formattedjson.append(singleSong)
                        except Exception as e:
                            print(f"Failed to input a song for some reason idk: {e}")
                dumpStr = dumps(formattedjson, indent=4)
                f.write(dumpStr)
def setupSession() -> requests.Session: # Gets the cookie
    newSession = requests.session()

    response = newSession.get("http://myspace.com")
    newCookies = (response.cookies.get_dict())
    html = response.text
    return newSession, newCookies

def setupCrawler():
    title = input("Input your search query: ")
    jsoned = input("Would you like this in a json file or txt file? (y for json, n for txt)")

    query = title
    if jsoned.lower() == "y":
        jsonToggle = True
    else:
        jsonToggle = False
    
    print("Starting :3")

if __name__ == "__main__":
    session, cookies = setupSession()

    if Setup == True:
        print("Session Successfully Started! (welcome to my very cool myspace crawler thingy!! it was heavily inspired by Cr1tika7's myspace crawler :3)\n\n")
        setupCrawler()
        sleep(1)

    newSearch = mySpace(session=session, cookies=cookies, query=query)
    newRequest = requests.get("http://myspace.com", cookies=cookies)

    SSid = newSearch.get_SSID()
    finishedCrawler = newSearch.mainCrawler()

    newSearch.finishAndFormatJson(finishedCrawler)
