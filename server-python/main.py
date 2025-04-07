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


# Set up location tool using Traccer api
def get_location(**kwargs):

    # Check to see if a specific time range is being used, if not get last known location
    if kwargs.get('from'):
        latest_location = False
    else:
        latest_location = True
    
    # Get device location using Traccar api
    response = requests.get(
        f'{traccar_base_url}/api/positions',
        params = ({"deviceId":4, "latest":latest_location, "from":kwargs.get('from'), "to":kwargs.get('to')}), 
        auth=(traccar_username, traccar_password), 
        headers={"Accept": "application/json"},
        timeout=10
    )

    # Extract and parse data from api reponse
    position_data = response.json()[0]

    lat = position_data.get('latitude')
    lon = position_data.get('longitude')
    alt = position_data.get('altitude')
    time = position_data.get('deviceTime')

    # Gets address from lat/long and return it using nominatim api
    add = (requests.get("https://nominatim.openstreetmap.org/reverse", {"format": "json", "lat": lat, "lon": lon, "email": traccar_username})).json()['display_name']

    return(f"Address: {add} Latitude: {lat} Longitude: {lon} Altitude: {alt} Time when logged: {time}") # Sends data back to main tool calling section of main loop



# Defines tools for ChatGPT
tools=[

    {
        "type": "web_search_preview"
    },
    {
        "type": "function",
        "name": "get_location",
        "description": "Uses Traccer to return the users last location, altitude, and time. You can filter for certain times if needed: \
                        put the date the user entered in 'from' and adding to the next of the lowest unit of time they specified for 'to'. \
                        So for 'Where was I on June 10th' you would filter 'from' June 10th 'to' June 11th, in correct time formatting, ISO 8601. \
                        Assume other info is current day/month/year unless otherwise specifeid. TIMES WILL BE GIVEN IN EST, BUT SERVER IS IN UTC, \
                        SO CONVERT. If different locations are recived, list the top ones and say there are others unless told otherwsie.'",
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

# Define base ChatGPT input
input_messages = [{"role": "system", "content": f"You are Aspen, a helpful personal assistant built for and by Linden Morgan. \
You can draw on differant data sources to accomplish this goal. Don't use markdown symbols. The current date/time is {datetime.now()}"}]


# ChatGPT interaction
while True:

    # Add user input to ChatGPT input
    user_input = input("User: ")
    input_messages.append({"role": "user", "content": user_input})

    # Generate ChatGPT response
    response = client.responses.create(
        model="gpt-4o-mini",
        tools=tools,
        input=input_messages
    )
    
    output_str = response.output_text # Find just text from response


    # Return response if tools aren't used, otherwise get use tools
    if str(output_str):
        input_messages.append({"role": "assistant", "content": output_str}) # Add ChatGPT response to input for history
        print(output_str) # Print final response

    else:
        input_messages.append(response.output[0]) # Add ChatGPT response to input for history
        for tool_call in response.output:
            if tool_call.type != "function_call":
                continue

            # Get tool call name and arguments
            name = tool_call.name
            kwargs = json.loads(tool_call.arguments)
            
            # Call tools
            try:
                if name == 'get_location':
                    result = (get_location(**kwargs))
            
            # Error handeling for tool calls
            except IndexError:
                if name == "get_location":
                    print("No location data in range.")
                    result = "No location data in range."
                else: 
                    print("Unkown error with tool calling.")
                    result = "Unkown error with tool calling."
                print(kwargs)
            except:
                if name == "get_location":
                    print("Unkown error accessing location data occuerd.")
                    result = "Unkown error accessing location data occuerd."
                else:
                    print("Unkown error with tool calling.")
                    result = "Unkown error with tool calling."


            # Add tool call results to input
            input_messages.append({
                "type": "function_call_output",
                "call_id": tool_call.call_id,
                "output": str(result)
            })

        # Get new response using tool info
        response_2 = client.responses.create(
            model="gpt-4o-mini",
            tools=tools,
            input=input_messages
        )

        # Add ChatGPT response to input for history
        input_messages.append({"role": "assistant", "content": response_2.output_text})

        # Print final response
        print(response_2.output_text)
