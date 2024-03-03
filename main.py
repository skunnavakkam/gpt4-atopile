import together
import requests
from bs4 import BeautifulSoup
import re
import PySpice
import atopile
import subprocess
import time

PROMPT = input("PROMPT: ")
together.api_key = "b7e20cb7b1acf926630a492fc67ba01ab30c0b481ef023f426a64ad0f93d5b9b"


#########################################
########### UTILITY FUNCTIONS ###########
#########################################


def web_search(query: str, cutoff=2) -> str:
    """
    Takes in a search query and returns a natural language response from scraping the web. Uses the Qwant search engine, and uses Nous Hermes to summarize the top 5 results.

    Args:
    query (str): The search query
    cutoff (int): The number of search results to summarize
    """
    base_url = "https://api.qwant.com/v3/search/web"
    params = {"q": query, "locale": "en_US", "t": "web"}
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    print("WEBSEARCH: MAKING SEARCH")
    response = requests.get(base_url, params=params, headers=header)
    items = response.json()["data"]["result"]["items"]["mainline"]
    for item in items:
        if item["type"] == "web":
            items = item["items"][0:cutoff]

    """
    Format of ITEM in ITEMS: <- only relevant info
    {'title': title,
    'favicon': favicon,
    'url': url,
    'urlPingSuffix': urlPingSuffix,
    'source': source}
    """

    text_list = []

    for index, item in enumerate(items):
        url = item["url"]
        url_response = requests.get(url, headers=header)
        soup = BeautifulSoup(url_response.text, "html.parser")
        text_list.append(
            re.sub(
                r"\n\s+",
                "\n",
                re.sub(r" +", " ", re.sub(r"\n{2,}", "\n", soup.get_text().strip())),
            )
        )
        print(f"WEBSEARCH: FETCHING {index + 1 } out of {cutoff + 1} URLS")

    joined_text = "\n".join(text_list)
    output = together.Complete.create(
        prompt=f'You are a concise, thorough, articulate genius. Your task is to summarize the following text so it can serve as a guide for another user to answer the query "{query}":\n{joined_text}\nSummary:\n',
        model="togethercomputer/Llama-2-7B-32K-Instruct",
        max_tokens=2048,
        temperature=0.2,
        top_k=60,
        top_p=0.6,
        repetition_penalty=1.1,
        stop=["\n\n"],
    )
    summary = output["output"]["choices"][0]["text"]

    return "The following is a summary of the top 5 search results \n\n" + summary


def write(code: str):
    """
    Takes in a code string, writes it to the .ato file, and compiles it

    Args:
    - code (str): The code to write to the .ato file

    """

    with open("project/elec/src/project.ato", "w") as file:
        file.write(code)
    res = subprocess.run(
        ["ato build"], shell=True, cwd="project", capture_output=True, text=True
    )

    stdout = res.stdout
    stderr = res.stderr
    print("RETURN CODE: ", res.returncode)

    return stdout


def SPICE():
    """
    Runs the PySpice environment
    """
    pass


#########################################
########### ACTION LOOP #################
#########################################

# load the prompt from assets/prompt.txt
with open("assets/prompt.txt", "r") as file:
    system_prompt = file.read()

system_prompt += PROMPT + "\n---\n"
past_actions = "<reasoning>"

print(f"Prompt: {PROMPT}")

while True:
    action = together.Complete.create(
        prompt=system_prompt + past_actions,
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        max_tokens=2048,
        temperature=0.4,
        top_k=80,
        top_p=0.8,
        repetition_penalty=1.18,
        stop=["</write>", "</reasoning>", "</websearch>"],
    )

    curr_action = action["output"]["choices"][0]["text"]
    past_actions += curr_action
    curr_action_type = re.findall(r"<([^<>]+)>", past_actions)[-1]
    past_actions += f"</{curr_action_type}>\n"

    print(curr_action_type)

    if curr_action_type == "write":
        print("RUNNING CODE")
        output = write(re.sub(r"<[^<>]+>", "", "<" + curr_action, count=1))
        print(output)
        past_actions += output
    elif curr_action_type == "websearch":
        print("SEARCHING WEB")
        output = web_search(re.sub(r"<[^<>]+>", "", "<" + curr_action, count=1))
        past_actions += output

    print(past_actions)

    past_actions += "<"
    if input("hit enter for next step") == "break":
        break
