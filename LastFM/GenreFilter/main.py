import requests
from time import sleep
from os import system, makedirs

trackName = "mental day notes" # search phrase, it will search for any title with this phrase IN the title, its pretty easy to change this script to make it exact tho
Searchtags = ["gaze"] # tags to filter, it checks to see if a tag has these words in it, so for example you can say "indie" and it will still catch "indie rock" or smth
maxListeners = 1000 # max listeners, set to some big number to remove this
startWithSetup = True # if you wanna use this with the setup in the beginning, set this to true, if you wanna skip it, set it to false

APIKey = ""  # Your LastFM API Key (Get one here https://www.last.fm/api/account/create, just label it anything, it doesn't matter too much!!)

## Don't edit aTempest - Open Your Eyesnything beyond this point unless you know what ur doing

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
    if len(tag) > 0:
        Searchtags = tagToTable(tagString=tag)
        print(Searchtags)
    else:
        Searchtags = []

def appendToResults(artist, track, link, listeners, MTags):
    try:
        makedirs("Results", exist_ok=True)
        with open(f"Results/{trackName.strip()}-{'-'.join(Searchtags)}.txt", "a") as f:
            f.write(f"{artist} - {track} [Listeners: {listeners}] (Matching Tags: {', '.join(MTags)}) ({link})\n\n")
    except Exception as e:
        print(f"Failed To Write song to file{e}")

def returnTracks(TrackSearch):
    while True:
        try:
            url = f"http://ws.audioscrobbler.com/2.0/?method=track.search&track={TrackSearch}&api_key={APIKey}&limit=10000&format=json"
            print(f"Getting tracks for trackname '{TrackSearch}'")
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
    if len(Searchtags) != 0:
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
    else:
        return {}

def filterTracks(trackTable):
    for en, track in enumerate(trackTable):
        artist = track.get("artist", "Unknown Artist")
        track_name = track.get("name", "Unknown Track")
        link = track.get("url", "Unknown Link")
        listeners = track.get("listeners", 0)
        checked = False

        if trackName.lower() in track_name.lower() and artist not in repeat and int(listeners) <= maxListeners: # change to (if trackName.lower() == track_name.lower() and artist not in repeat and int(listeners) <= maxListeners:) if you want it to only equal the seardch term
            while not checked:
                tags = getTags(artist=artist)
                try:
                    if "toptags" in tags and "tag" in tags["toptags"] or len(Searchtags) == 0:
                        matchingTags = []
                        search_tags_lower = []
                        if len(Searchtags) != 0:
                            tag_list = [tag["name"].lower() for tag in tags["toptags"]["tag"]]
                            search_tags_lower = [tag.lower() for tag in Searchtags]
                            
                            

                            for search_tag in search_tags_lower:
                                for tag in tag_list:
                                    if search_tag in tag:
                                        matchingTags.append(tag)
                                        break
                        if len(matchingTags) == len(search_tags_lower):
                            foundTab.append(f"{artist} - {track_name}")
                            repeat.append(artist)
                            appendToResults(artist=artist, track=track_name, link=link, listeners=listeners, MTags=matchingTags)
                    
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
