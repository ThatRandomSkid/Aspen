import os
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

# Set up variables 
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
traccar_base_url = os.getenv("TRACCAR_BASE_URL")
traccar_username = os.getenv("TRACCAR_USERNAME")
traccar_password = os.getenv("TRACCAR_PASSWORD")

device_id = 4


# Get Traccar info via api
def get_location(**kwargs):

    if kwargs.get('from'):
        latest_location = False
    else:
        latest_location = True
    
    response = requests.get(

        f'{traccar_base_url}/api/positions',
        params = ({"deviceId":4, "latest":latest_location, "from":kwargs.get('from'), "to":kwargs.get('to')}), 
        auth=(traccar_username, traccar_password), 
        headers={"Accept": "application/json"},
        timeout=10
    )

    data = response.json()
    position_data = data[0]


    
    lat = position_data.get('latitude')
    lon = position_data.get('longitude')
    alt = position_data.get('altitude')
    add = (requests.get("https://nominatim.openstreetmap.org/reverse", {"format": "json", "lat": lat, "lon": lon, "email": traccar_username})).json()
    time = position_data.get('deviceTime')

    location = f"Address: {add} \nLatitude: {lat}\nLongitude: {lon}\nAltitude: {alt}\nTime when logged: {time}"
    
    return(location)

# Function for running tools
def call_tools(name, kwargs):
    if name == 'get_location':
        return(get_location(**kwargs))


# Defines tools for ChatGPT
tools=[

    {
        "type": "web_search_preview"
    },
    {
        "type": "function",
        "name": "get_location",
        "description": "Uses Traccer to return the users last location, altitude, and time. \
                        You can filter for certain times if needed: put the date the user entered in \
                        'from' and adding to the next of the lowest unit of time they specified for 'to'. So for 'Where was I on June 10th' \
                        you would filter 'from' June 10th 'to' June 11th, in correct time formatting, ISO 8601. Assume other info is current day/month/year \
                        unless otherwise specifeid. Times will be in EST, but responses are in UTC, so convert. If different locations are recived, list the top ones \
                        and say there are others unless told otherwsie.'",
        "parameters": {
            "type": "object",
            "properties": {
                "from":{
                    "type": "string",
                    "description": "the from part of the time filter, in ISO 8601"
                },
                "to":{
                    "type": "string",
                    "description": "the to part of the time filter, in ISO 8601"
                }

            },
            "required": []
        }
    }   
]

# ChatGPT interaction
while True:
    user_input = input("User: ")

    input_messages = [{"role": "system", "content": f"You are Aspen, a helpful personal assistant for Linden Morgan. \
                       You can draw on differant data sources to accomplish this goal. The current date/time is {datetime.now()}\
                       Don't use markdown symbols."}, {"role": "user", "content": user_input}]

    response = client.responses.create(
        model="gpt-4o-mini",
        tools=tools,
        input=input_messages
    )

    # Get tools if needed, otherwise return response
    if type(response) is str:
        print(response)
    else:
        input_messages.append(response.output[0])
        for tool_call in response.output:
            if tool_call.type != "function_call":
                continue

            name = tool_call.name

            #print(tool_call)

            kwargs = json.loads(tool_call.arguments)
            
            try:
                result = call_tools(name, kwargs)
            except IndexError:
                print("No location data in range.")
                result = None
            except:
                print("Unkown error with location parsing.")
                result = None

            input_messages.append({
                "type": "function_call_output",
                "call_id": tool_call.call_id,
                "output": str(result)
            })
        # Get response with tool info
        response_2 = client.responses.create(
            model="gpt-4o-mini",
            tools=tools,
            input=input_messages
        )
        print(response_2.output_text)