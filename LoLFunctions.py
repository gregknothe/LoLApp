import requests
import shutil
import json
import sys
import pandas as pd
import datetime
import os
from PIL import Image

apiKey = "RGAPI-7a0a08d9-8fee-4503-abe9-57ed137acd9f"
os.chdir(sys.path[0])


def updateGameVersion():
    #Updates the current version to the live version of the game (ex. 11.3.1 -> 11.3.2)
    version = requests.get("https://ddragon.leagueoflegends.com/api/versions.json").json()
    liveVersion = version[0]
    f = open("Assets/version.txt","r")
    currentVersion = f.read()
    if liveVersion != currentVersion:
        print "Different patch"
        f.close()
        f = open("Assets/version.txt","w")
        f.truncate(0)
        f.write(str(liveVersion))
    f.close()
    return 0
#updateGameVersion()


def getGameVersion():
    #Gets the current game version from the text file
    f = open("Assets/version.txt", "r")
    currentVersion = f.read()
    f.close()
    return currentVersion


def userInfo(userName="shuckle", region="na1"):
    #Gets account info from userName and region
    serverList = "br1", "euw1", "eun1", "jp1", "la1", "la2", "na1", "kr", "oc1", "ru", "tr1"
    if region not in serverList:
        sys.exit("Non-valid Region:" + region)
    requestUrl = "https://" + region + ".api.riotgames.com/lol/summoner/v4/summoners/by-name/" + userName + "?api_key=" + apiKey
    rawJson = requests.get(requestUrl)
    if str(rawJson) != "<Response [200]>":
        sys.exit("Invalid Request: " + str(rawJson))
    j = rawJson.json()
    return j["name"], j["accountId"], j["summonerLevel"], j["profileIconId"], j["puuid"], j["id"]
#print userInfo("megablaziken", "na1")


def championName(championIdList=["266", "103", "142"]):
    #Converts champion id to champion name
    championKey = requests.get("https://ddragon.leagueoflegends.com/cdn/" + getGameVersion() + "/data/en_US/champion.json").json()
    championNameList = []
    championPngList = []
    for y in championIdList:
        for x in championKey["data"].keys():
            if championKey["data"][x]["key"] == y:
                championNameList.append(championKey["data"][x]["name"])
                championPngList.append(championKey["data"][x]["image"]["full"])
    return championNameList, championPngList
#print championName()


def roleIdentifier(role="NONE", lane="JUNGLE"):
    #Assigns role to the player/game
    if lane == "JUNGLE" or lane == "NONE":
        return "JUNGLE"
    elif role == "DUO_CARRY":
        return "ADC"
    elif role == "DUO_SUPPORT":
        return "SUPPORT"
    elif lane == "MID":
        return "MID"
    elif lane == "TOP":
        return "TOP"


def userMatchHistory(userId="uYQ9WlRX_u1DT-Ugn_RSCr7D6R8wHZmGRwI5881wI2QvyA", region="na1"):
    #Gets the match history of the player (mainly the matchId, queueType and champ)
    requestUrl = "https://" + region + ".api.riotgames.com/lol/match/v4/matchlists/by-account/" + userId + "?api_key=" + apiKey
    rawJson = requests.get(requestUrl)
    if str(rawJson) != "<Response [200]>":
        sys.exit("Match History Not Found: " + str(rawJson))
    summonersRift = [400, 420, 430, 440]
    #Normal Draft(400), Ranked Solo(420), Normal Blind(430), Ranked Flex(440), Aram(450)
    matchHistory = rawJson.json()
    try:
        matchCount = len(matchHistory["matches"])
    except:
        sys.exit("No Matches Available")

    gameId = []
    queueType = []
    champId = []
    champName = []
    timeStamp = []
    date = []
    role = []
    lane = []

    for x in range(0,matchCount):
        currentMatch = matchHistory["matches"][x]
        if currentMatch["queue"] in summonersRift:
            gameId.append(currentMatch["gameId"])
            queueType.append(currentMatch["queue"])
            champId.append(str(currentMatch["champion"]))
            timeStamp.append(currentMatch["timestamp"])
            date.append(datetime.datetime.fromtimestamp(currentMatch["timestamp"]/1000.0))
            role.append(currentMatch["role"])
            lane.append(currentMatch["lane"])
    champInfo = championName(champId)
    champName = champInfo[0]
    champPng = champInfo[1]
    df = pd.DataFrame(list(zip(gameId, queueType, champId, champName, champPng, timeStamp, date, role, lane)), columns=["gameId", "queueType", "champId", "champName", "champPng", "timeStamp", "date", "role", "lane"])
    return df
#print userMatchHistory(userId="QNBtKL-gS3xoXHeipY4JCPF_AS0GyYz0nBJyrEJbDT_JVw")


def getChampPng(champPng="Swain.png"):
    #Checks to see if champ icon is already saved, if not, it retreives it and saves it.
    requestUrl = "https://ddragon.leagueoflegends.com/cdn/" + getGameVersion() + "/img/champion/" + champPng
    assetLocation = "Assets/champPng/" + champPng
    try:
        #Attempt to open file (to see if it exist)
        fileCheck = open(assetLocation)
        fileCheck.close()
    except IOError:
        #Creates file if it is missing
        request = requests.get(requestUrl, stream = True)
        request.raw.decode_content = True
        with open(assetLocation, "wb") as f:
            shutil.copyfileobj(request.raw, f)
    return 0 #Or the image it self, idk what i want atm
#getChampPng("TwistedFate.png")


def getChampSpell(champName="Aatrox"):
    #WIP: Get spell icons for given champ (might not actually want/need)
    requestUrl = "https://ddragon.leagueoflegends.com/cdn/" + getGameVersion() + "/data/en_US/champion/" + champName + ".json"
    champSpellFolder = "Assets/champSpells/" + champName
    if os.path.isdir(champSpellFolder):
        print("it exists")
    else:
        print("Nope")
        os.mkdir(champSpellFolder)   
    return 0
#getChampSpell()