import requests
from pyowm import OWM
from pyowm.utils import config
from pyowm.utils import timestamps

api_key = ''

base_url = "http://api.openweathermap.org/data/2.5/weather?"

# Give city name
city_name = ('Ecublens,CH')

# complete_url variable to store
# complete url address
complete_url = base_url + "appid=" + api_key + "&q=" + city_name

# get method of requests module
# return response object
response = requests.get(complete_url)

# json method of response object
# convert json format data into
# python format data
x = response.json()
print(x)
print(f"couverture de nuages: {x['clouds']['all']}%")
