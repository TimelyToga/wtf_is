from django.shortcuts import render
from django.http import HttpResponseRedirect

from bs4 import BeautifulSoup as bs
import requests
import json


WIKI_PAGE_BASE = "https://en.wikipedia.org/wiki/"

WIKI_API = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&titles="


def home(request):
    return render(request, "home.html", context={})


def about(request):
    return render(request, "about.html", context={"term": "about_page"})


def definition(request, term):
    context = {"term": term, "link": WIKI_PAGE_BASE + term}

    # Get definition from Wikipedia
    wiki_def = api_fs(term)
    if wiki_def:
        context["def"] = wiki_def

    return render(request, "definition.html", context=context)


def search(request):
    parameter = request.GET.get("search", "")

    if parameter:
        # Check to make sure it is a Wikipedia page
        return HttpResponseRedirect("/is/" + parameter)



def scrape_site_fs(term):
    rdata = requests.get(WIKI_PAGE_BASE + term)

    soup = bs(rdata.content)

    page_content = soup.find("div", {"id": "mw-content-text"})

    if page_content:
        return page_content.findAll("p")[:5]

    return None


def api_fs(term):
    rdata = requests.get(WIKI_API + term).content

    json_data = json.loads(rdata)

    if json_data:
        pages = json_data["query"]["pages"]
        page_keys = pages.keys()

        return pages[page_keys[0]]["extract"]



