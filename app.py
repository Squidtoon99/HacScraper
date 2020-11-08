from flask import Flask, render_template, redirect, url_for, request, jsonify
import requests
from bs4 import BeautifulSoup
from subprocess import Popen, PIPE
from urllib.parse import urlparse
from pymongo import MongoClient
from timeloop import Timeloop
from datetime import timedelta


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


# @app.route("/user/<user>/<course>")
# def coursepage(user, course):
#     user = db.Users.find_one({"doctype": "user", "username": user})

#     if user:
#         course = db.Courses.find_one(
#             {"user_id": str(user["_id"]), "id": course, "doctype": "course"}
#         )
#         if not course:
#             return redirect("../")

#         assignments = [doc for doc in db.Assignments.aggregate([
#             {'$match':{'user_id':str(user['_id']), 'course.id':str(course['id']),'doctype':'assignment'}},
#             {'$sort':{'date_due',-1}},
#         ])]

#         if assignments:
#             lowestGrade = min(assignments, key=lambda a: a["score"])

#             mostRecentGrade = next(filter(lambda a: a["score"], assignments))
#         else:
#             lowestGrade, mostRecentGrade = None

#         grades = [a.get("score") for a in assignments]
#         if len(grades) == 1:
#             grades = grades * 2

#         empty = ["''"] * len(grades)
#         empty = ",".join(empty)
#         grades = ",".join(grades)

#         return render_template(
#             "user.html",
#             **{
#                 "user": user,
#                 "course": course,
#                 "assignments": assignments,
#                 "count": len(assignments),
#                 "low": lowestGrade,
#                 "recent": mostRecentGrade,
#                 "grades": grades,
#                 "empty": empty,
#             },
#         )


@app.route("/user/<user>")
def userPage(user):
    user = db.Users.find_one({"doctype": "user", "username": user})
    if user:
        courses = [
            i
            for i in db.Courses.find({"user_id": str(user["_id"]), "doctype": "course"})
        ]

        for c in courses:
            if not c["grade"]:
                c["grade"] = 100
            else:
                c["grade"] = str(c["grade"])

        assignments = [
            i
            for i in db.Assignments.find(
                {"user_id": str(user["_id"]), "doctype": "assignment"}
            ).sort("date_due", -1)
        ]

        for a in assignments:
            a["score"] = str(a["score"])
        if not courses or not assignments:
            return

        lowestGrade = min(courses, key=lambda course: course["grade"])
        mostRecentGrade = min(
            filter(lambda a: a["score"], assignments),
            key=lambda course: course["score"],
        )

        grades = [a.get("score") for a in assignments]
        if len(grades) == 1:
            grades = grades * 2

        empty = ["''"] * len(grades)
        empty = ",".join(empty)
        grades = ",".join(grades)

        return render_template(
            "user.html",
            **{
                "user": user,
                "courses": courses,
                "assignments": assignments,
                "count": len(courses),
                "low": lowestGrade,
                "recent": mostRecentGrade,
                "grades": grades,
                "empty": empty,
            },
        )

    else:
        return redirect("/")


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

    scrapeNonJob()

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


tl = Timeloop()


@tl.job(interval=timedelta(seconds=60))
def scrape():
    process = Popen(["py", "HacSpyder"], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()


def scrapeNonJob():
    process = Popen(["py", "HacSpyder"], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()


if __name__ == "__main__":
    app.run("localhost", 80)

    tl.start(block=True)