import urllib
import json

		
def instructions(keys,dbport):
	from utilities import getArtistInfo
	from htmlgenerators import artistLink, artistLinks, trackLink, scrobblesArtistLink, keysToUrl, pickKeys, clean
	
	clean(keys)
	timekeys = pickKeys(keys,"since","to","in")
	limitkeys = pickKeys(keys)
	
	# get chart data
	response = urllib.request.urlopen("http://[::1]:" + str(dbport) + "/charts/artists?" + keysToUrl(timekeys,limitkeys))
	db_data = json.loads(response.read())
	charts = db_data["list"][:50]
	topartist = charts[0]["artist"]
	
	info = getArtistInfo(topartist)
	imgurl = info.get("image")
	pushresources = [{"file":imgurl,"type":"image"}] if imgurl.startswith("/") else []
	
	# get total amount of scrobbles
	response = urllib.request.urlopen("http://[::1]:" + str(dbport) + "/scrobbles?" + keysToUrl(timekeys,limitkeys))
	db_data = json.loads(response.read())
	scrobblelist = db_data["list"]
	scrobbles = len(scrobblelist)
	
	
	# build list
	maxbar = charts[0]["scrobbles"]
	
	i = 1
	html = "<table class='list'>"
	for e in charts:
		html += "<tr>"
		html += "<td class='rank'>#" + str(i) + "</td>"
		html += "<td class='artist'>" + artistLink(e["artist"])
		if (e["counting"] != []):
			html += " <span class='extra'>incl. " + ", ".join([artistLink(a) for a in e["counting"]]) + "</span>"
		html += "</td>"
		html += "<td class='amount'>" + scrobblesArtistLink(e["artist"],timekeys,amount=e["scrobbles"],associated=True) + "</td>"
		html += "<td class='bar'>" + scrobblesArtistLink(e["artist"],timekeys,percent=e["scrobbles"]*100/maxbar,associated=True) + "</td>"
		html += "</tr>"
		i += 1
	html += "</table>"

	replace = {"KEY_TOPARTIST_IMAGEURL":imgurl,"KEY_SCROBBLES":str(scrobbles),"KEY_ARTISTLIST":html}

	return (replace,pushresources)