from flask import Flask, render_template, redirect, url_for, request, jsonify
import requests
from bs4 import BeautifulSoup
from subprocess import Popen, PIPE
from urllib.parse import urlparse
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient()
db = client.Main


@app.route("/")
def index():
    users = [i for i in db.Users.find({"doctype": "user"})]
    return render_template("index.html", **{"users": users})


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/user/<user>")
def userPage():
    pass


@app.route("/add_user", methods=["POST", "GET"])
def add_user():
    if request.method == "GET":
        return redirect("/")

    o = urlparse(request.form["url"])  # the actual url for auth stuff
    url = f"{o.scheme or 'https'}://{o.netloc}"

    db.Users.find_one_and_update(
        {"doctype": "user", "username": request.form["username"]},
        {
            "$set": {
                "password": request.form["password"],
                "name": request.form["name"],
                "url": url,
            }
        },
        upsert=True,
    )
    return redirect("/")
    # url = request.form["url"]
    # base = [
    #     "__RequestVerificationToken",
    #     "SCKTY00328510CustomEnabled",
    #     "SCKTY00436568CustomEnabled",
    #     "Database",
    #     "VerificationOption",
    #     "tempUN",
    #     "tempPW",
    # ]
    # headers = {
    #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0",
    #     "Upgrade-Insecure-Requests": "1",
    #     "Accept-Language": "en-US,en;q=0.5",
    #     "Connection": "keep-alive",
    #     "Host": url,
    #     "Origin": url,
    #     "Referrer": f"https://{url.replace('https://','').replace('http://','')}/HomeAccess/Account/LogOn?ReturnUrl=%2fHomeAccess%2f",
    # }
    # with requests.Session() as session:
    #     try:
    #         o = urlparse(url)  # the actual url for auth stuff
    #         url = f"{o.scheme or 'https'}://{o.netloc or url}/HomeAccess/Account/LogOn"
    #     except:
    #         return jsonify(error="invalid uri")
    #     print(url)

    #     resp = session.get(
    #         "https://hac.coppellisd.com/HomeAccess/Account/LogOn?ReturnUrl=%2fHomeAccess%2f",
    #         headers=headers,
    #     )
    #     o = urlparse(resp.url)  # the actual url for auth stuff
    #     url = f"{o.scheme or 'https'}://{o.netloc}"

    #     soup = BeautifulSoup(resp.content, "html.parser")
    #     # print(soup.prettify())
    #     session.headers.update(
    #         {
    #             "Host": o.netloc,
    #             "Origin": url,
    #             "Referrer": url
    #             + "/HomeAccess/Account/LogOn?ReturnUrl=%2fHomeAccess%2f",
    #         }
    #     )

    #     # print([soup.find(id=v)["value"] for v in base if soup.find(id=v)])
    #     data = {
    #         **{v: (soup.find(attrs={"name": v}) or {}).get("value") for v in base},
    #         "LogOnDetails.UserName": request.form["username"],
    #         "LogOnDetails.Password": request.form["password"],
    #     }

    #     new_data = session.post(
    #         url
    #         + "/HomeAccess/Account/LogOn?ReturnUrl=%2fHomeAccess%2fAccount%2fDetails",
    #         allow_redirects=True,
    #     )

    #     soup = BeautifulSoup(new_data.content, "html.parser")

    #     name = soup.find(id="plnMain_lblName")

    #     return name or "hmm is that right?"


if __name__ == "__main__":
    app.run("localhost", 80)

    process = Popen(["py", "HacSpyder"], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
