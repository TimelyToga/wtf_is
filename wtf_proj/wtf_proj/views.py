from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse

from bs4 import BeautifulSoup as bs
import requests
import json


WIKI_PAGE_BASE = "https://en.wikipedia.org/wiki/"

WIKI_API_BASE = "https://en.wikipedia.org/w/api.php?format=json&action=query"

WIKI_EXTRACT = WIKI_API_BASE + "&prop=extracts&exintro=&explaintext=&titles="

WIKI_SEARCH = WIKI_API_BASE + "&list=search&meta=&titles=&utf8=1&srinfo=suggestion|totalhits&srsearch="


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

    else:
        return HttpResponseRedirect("/search_results/?term=" + term)

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
    print(WIKI_EXTRACT + term)
    rdata = requests.get(WIKI_EXTRACT + term).content

    json_data = json.loads(rdata)

    if not json_data:
        # perform search
        return HttpResponseRedirect("/search_results/?term=" + term)

    # Get the pages from the results
    pages = json_data["query"]["pages"]
    page_keys = pages.keys()

    if int(page_keys[0]) == -1:
        return None

    first_page = pages[page_keys[0]]

    if not first_page:
        # If no first page, perform search
        return None

    return first_page["extract"]


def search_for_results(request):
    term = request.GET.get("term", "")

    j_data = json_request(WIKI_SEARCH + term)

    context = {}

    if not j_data:
        # Issue an error
        return HttpResponse("Wikipedia didn't send back JSON when you searched for " + term + " . Pls try again.")

    query = j_data["query"]
    search_info = query["searchinfo"]
    search = query["search"]

    if len(search) == 0 or int(search_info["totalhits"]) == 0:
        context["failed_search"] = True

        if "suggestion" in search_info.keys():
            # offer suggestion
            context["suggestion"] = search_info["suggestion"]
        else:
            # report search failure
            context["failed_search"] = True

    else:
        # Display the search results
        context["results"] = search

    return render(request, "search_results.html", context=context)


def json_request(url):
    rdata = requests.get(url).content

    return json.loads(rdata)
