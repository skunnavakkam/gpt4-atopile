from flask import Flask, render_template, request
import requests
import json
from openai import OpenAI
# import pretty print
from pprint import pprint

app = Flask(__name__)

current_transcript = ""
current_notes = ""
client = None
prompt = ""


@app.route("/")
def home():
    return render_template("home.html", transcript="")


# take in a post request
@app.route("/", methods=["POST"])
def design():
    openai_key = request.form["openai_key"]
    prompt = request.form["prompt"]
    client = OpenAI(openai_key, base_url="https://api.together.xyz")
    return "Form data received and printed in the console."


def search(query: str) -> str:
    # format the query
    base_url = "https://api.qwant.com/v3/search/web"
    params = {"q": query, "locale": "en_US", "t": "web"}
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(base_url, params=params, headers=header)
    items = response.json()["data"]["result"]["items"]["mainline"][2][0:3]
    for item in items:
        pass
    return items


def component_search(query: str) -> str:
    pass


if __name__ == "__main__":
    app.run(debug=True)

def prompt(previous_transcript: str) -> str:
