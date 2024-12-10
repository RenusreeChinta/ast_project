import requests

class WeatherAPI:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_weather(self, location):
        url = f"http://api.weather.com/data?location={location}&key={self.api_key}"
        response = requests.get(url)
        return response.json()

def print_weather(location, api_key):
    weather = WeatherAPI(api_key)
    data = weather.get_weather(location)
    print(data)
