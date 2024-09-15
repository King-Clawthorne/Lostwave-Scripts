import json
import requests
from time import sleep
from os import system

trackName = "where am i" #search phrase
Searchtags = ["punk", "british"] #tags to filter
maxListeners = 1000 #max listeners, set to some big number to remove this

APIKey = ""  # Your LastFM API Key

foundTab = []
repeat = []

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

def filterTracks(trackTable):
    for en, track in enumerate(trackTable):
        artist = track.get("artist", "Unknown Artist")
        track_name = track.get("name", "Unknown Track")
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
                    
                    checked = True
                except Exception as e:
                    print(f"Error: {e}")
                    sleep(15)

        system("cls")
        print(f"{en} - {len(trackTable)}")

        for thing in foundTab:
            print(thing)




if __name__ == "__main__":
    tracks = returnTracks(TrackSearch=trackName)
    if 'results' in tracks and 'trackmatches' in tracks['results']:
        trackMatches = tracks['results']['trackmatches']['track']
        filterTracks(trackMatches)
    else:
        print("No track matches found.")
