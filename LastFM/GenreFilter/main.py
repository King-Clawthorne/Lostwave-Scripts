import requests
from time import sleep
from os import system, makedirs

trackName = "Mental Day Notes" # search phrase
Searchtags = ["gaze"] # tags to filter
maxListeners = 10000 # max listeners, set to some big number to remove this
startWithSetup = True # if you wanna use this with the setup in the begining, set this to true, if you wanna skip it, set it to false

APIKey = "839468de11b1008ae280e3fbf436e10"  # Your LastFM API Key (Get one here https://www.last.fm/api/account/create, just label it anything, doesn't matter too much!!)

foundTab = []
repeat = []

def Setup():
    system("cls")
    def tagToTable(tagString : str):
        return tagString.strip().split(",")

    global trackName
    global Searchtags
    print("Via's last.fm Searcher!! (set up the api key in the 'GenreFilter.py' file if you haven't already!)")
    trackNameInput = input("Type search query here: ")
    trackName = trackNameInput

    # input the tags (waow)
    tag = input("Type tags here seperated by commas: ")
    Searchtags = tagToTable(tagString=tag)
    print(Searchtags)

def appendToResults(artist, track, link):
    try:
        makedirs("Results", exist_ok=True)
        with open(f"Results/{trackName.strip()}-{'-'.join(Searchtags)}.txt", "a") as f:
            f.write(f"{artist} - {track} ({link})\n\n")
    except Exception as e:
        print(f"Failed To Write song to file{e}")

def returnTracks(TrackSearch):
    while True:
        try:
            url = f"http://ws.audioscrobbler.com/2.0/?method=track.search&track={TrackSearch}&api_key={APIKey}&limit=10000&format=json"
            print(url)
            response = requests.get(url=url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                print("Rate limited. Waiting 15 seconds...")
                sleep(15)
            else:
                print(f"Error in returnTracks: {e}")
                break
        except Exception as e:
            print(f"Unexpected error in returnTracks: {e}")
            break

def getTags(artist):
    while True:
        try:
            url = f"http://ws.audioscrobbler.com/2.0/?method=artist.gettoptags&artist={artist}&api_key={APIKey}&format=json"
            response = requests.get(url=url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                print("Rate limited. Waiting 15 seconds!!")
                sleep(15)
            else:
                print(f"Error in getTags: {e}")
                return {}
        except Exception as e:
            print(f"Unexpected error in getTags: {e}")
            return {}

def checkStreaming(Track, Artist):
    pass

def filterTracks(trackTable):
    for en, track in enumerate(trackTable):
        artist = track.get("artist", "Unknown Artist")
        track_name = track.get("name", "Unknown Track")
        link = track.get("url", "Unknown Link")
        listeners = track.get("listeners", 0)
        checked = False

        if trackName.lower() in track_name.lower() and artist not in repeat and int(listeners) <= maxListeners:
            while not checked:
                tags = getTags(artist=artist)
                try:
                    if "toptags" in tags and "tag" in tags["toptags"]:
                        tag_list = [tag["name"].lower() for tag in tags["toptags"]["tag"]]
                        search_tags_lower = [tag.lower() for tag in Searchtags]

                        if all(any(search_tag in tag for tag in tag_list) for search_tag in search_tags_lower):
                            foundTab.append(f"{artist} - {track_name}")
                            repeat.append(artist)
                            appendToResults(artist=artist, track=track_name, link=link)
                    
                    checked = True
                except Exception as e:
                    print(f"Error: {e}")
                    sleep(15)

        system("cls")
        print(f"{en} - {len(trackTable)}")

        for thing in foundTab:
            print(thing)




if __name__ == "__main__":
    if startWithSetup:
        Setup()
    tracks = returnTracks(TrackSearch=trackName)
    try:
        if 'results' in tracks and 'trackmatches' in tracks['results']:
            trackMatches = tracks['results']['trackmatches']['track']
            filterTracks(trackMatches)
        else:
            print("No track matches found.")
    except TypeError as e:
        print(f"exepction {e}\nIs your api key correct?")