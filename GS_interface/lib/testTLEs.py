# -*- coding: utf-8 -*-
"""
Created on Sat Sep 16 11:58:24 2023

@author: lgtle
"""
import requests


def download_tle_data(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            tle_data = response.text
            return tle_data
        else:
            print(
                f"Failed to download TLE data from {url}. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


# Example URL from CelesTrak for the ISS
url = "https://www.celestrak.com/NORAD/elements/stations.txt"
tle_data = download_tle_data(url)

with open("ISS.tle", "w") as file:
    file.write(tle_data)
