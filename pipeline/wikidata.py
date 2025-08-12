# pipeline/wikidata.py
import requests

def wikidata_search(label: str, lang="en", limit=1):
    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action":"wbsearchentities","format":"json",
        "language": lang, "search": label, "limit": limit
    }
    try:
        r = requests.get(url, params=params, timeout=8)
        r.raise_for_status()
        data = r.json().get("search", [])
        return [{"id":x["id"], "label":x.get("label",""), "desc":x.get("description","")} for x in data]
    except Exception:
        return []
