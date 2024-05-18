from flask import Flask
from dotenv import load_dotenv
import os
import requests
import re

app = Flask(__name__)

load_dotenv()
username = os.getenv("USERNAME")
email = os.getenv("EMAIL")
passwd = os.getenv("PASSWD")
server_id = os.getenv("SERVER_ID")
realms_url = "https://pc.realms.minecraft.net"


def get_endpoint(endpoint):
    global credentials
    header = {
        "Authorization": "Bearer {}".format(credentials["access_token"]),
        "Cookie": "sid=token:{}:{};user={};version=1.20.6".format(
            credentials["access_token"], credentials["uuid"], credentials["username"]
        ),
    }
    res = requests.get(realms_url + endpoint, headers=header)
    return res.json()


def get_credentials():
    s = requests.Session()

    url = "https://login.live.com/oauth20_authorize.srf?client_id=000000004C12AE6F&redirect_uri=https://login.live.com/oauth20_desktop.srf&scope=service::user.auth.xboxlive.com::MBI_SSL&display=touch&response_type=token&locale=en"
    res = s.get(url).text
    urlPost = re.search("urlPost:'.+?'", res, flags=0).group(0)[9:-1]
    k = re.search("sFTTag:'.*'", res).group(0)
    value = re.search('value=".+?"', k).group(0)[7:-1]

    body = {"login": email, "loginfmt": "email", "passwd": passwd, "PPFT": value}
    header = {"Content-Type": "application/x-www-form-urlencoded"}
    res = s.post(urlPost, data=body, headers=header, allow_redirects=True)
    # print(res.url)
    params = res.url.split("#")[1]
    params = params.split("&")
    access_token = ""

    # get access_token
    for i in params:
        if "access_token" in i:
            access_token = i.split("=")[1]
            break

    # sign into Xbox Live
    url = "https://user.auth.xboxlive.com/user/authenticate"
    obj = {
        "Properties": {
            "AuthMethod": "RPS",
            "SiteName": "user.auth.xboxlive.com",
            "RpsTicket": access_token,
        },
        "RelyingParty": "http://auth.xboxlive.com",
        "TokenType": "JWT",
    }

    res = requests.post(url, json=obj)
    json = res.json()
    token = json["Token"]
    uhs = json["DisplayClaims"]["xui"][0]["uhs"]

    # get XSTS token
    url = "https://xsts.auth.xboxlive.com/xsts/authorize"
    obj = {
        "Properties": {
            "SandboxId": "RETAIL",
            "UserTokens": [token],
        },
        "RelyingParty": "rp://api.minecraftservices.com/",
        "TokenType": "JWT",
    }
    res = requests.post(url, json=obj)
    token = res.json()["Token"]

    # login to mc via xbox
    url = "https://api.minecraftservices.com/authentication/login_with_xbox"
    obj = {
        "identityToken": "XBL3.0 x={};{}".format(uhs, token),
        "ensureLegacyEnabled": True,
    }
    res = requests.post(url, json=obj)
    json = res.json()
    access_token = json["access_token"]

    # MINECRAFT ACCESS TOKEN ACQUIRED (access_token)
    #
    # next, get uuid

    url = "https://api.mojang.com/users/profiles/minecraft/" + username
    json = requests.get(url).json()
    uuid = json["id"]

    # return credentials

    return {"uuid": uuid, "access_token": access_token, "username": username}


credentials = get_credentials()


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/players")
def get_players():
    try:
        res = get_endpoint("/worlds/" + server_id)
        online = []
        all_players = []
        for player in res["players"]:
            if player["online"]:
                online.append(player["name"])
            all_players.append(player["name"])
        return {"online": online, "all_players": all_players}
    except Exception as e:
        print(e)  # probably token expiration
        print("-------------------- retrying --------------------")
        global credentials
        credentials = get_credentials()
        return "<p>error</p>"


#        return get_players()

# try api, catch get refresh api key
