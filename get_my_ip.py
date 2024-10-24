#!/usr/bin/python3


import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# URL of the page
url = "https://test-01.cloudlabs.juniper.net/"

# Send a request to fetch the page content with SSL verification disabled
response = requests.get(url, verify=False)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the h1 tag that contains the IP address (it's the second h1 on the page)
    ip_address = soup.find_all('h1')[1].text.strip()
    
    print(f"IP Address: {ip_address}")
else:
    print(f"Failed to access the page, status code: {response.status_code}")

