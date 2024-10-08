import os
import requests
import json
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

def handler(event, context):
    '''
    Entry point for Lambda function
    '''

    # Verify the cryptographic Signature
    if not verify(event):
        return {'statusCode': 401, 'body': json.dumps('Unauthorized')}

    body = json.loads(event['body'])

    if body['type'] == 1:
        return {'statusCode': 200, 'body': json.dumps({'type': 1})}
    else:
        return interact(body)


def interact(raw_request):
    '''
    Handle the interaction request
    '''

    # Discord sends a request based on the slash command entered
    # This will intepret the request
    # Store Interactions TOKEN and ID
    os.environ["INTERACTIONS_TOKEN"] = raw_request["token"]
    os.environ["INTERACTIONS_ID"] = raw_request["id"]

    # Immediately send an interaction response back to discord to prevent a timeout
    send()

    data = raw_request["data"]
    userID = raw_request["member"]["user"]["id"]

    print(f"The Interaction Was Executed By User: {userID}")
    print(f"Full Interactions Structure {data}")

    # The command being executed
    command_name = data["name"]

    match command_name:
        # Command /chat [arg1: message]
        case "joke":
            

        # Command /dog
        # Sends a link embedded within the link's image of a dog   
        case "dog":
            message_content = requests.get("https://dog.ceo/api/breeds/image/random").json().get("message")
            update(message_content)

    return {}

def verify(event):
    '''
    Validates the request signature. This makes sure that the Interactions API request is coming from Discord
    '''
    signature = event['headers']['x-signature-ed25519']
    timestamp = event['headers']['x-signature-timestamp']
    verify_key = VerifyKey(bytes.fromhex(os.environ.get("DISCORD_PUBLIC_KEY")))
    message = timestamp + event['body']

    try:
        verify_key.verify(message.encode(), signature=bytes.fromhex(signature))
    except BadSignatureError:
        print("Bad signature")
        return False
    return True

# Utility Functions For Discord API
def send():
    url = f"https://discord.com/api/interactions/{os.getenv('INTERACTIONS_ID')}/{os.getenv('INTERACTIONS_TOKEN')}/callback"
    response = requests.post(url, json={"type": 5})
    
    print("Response status code: ")
    print(response.status_code)
    print(response.text)

def update(message):
    url = f"https://discord.com/api/webhooks/{os.getenv('DISCORD_ID')}/{os.getenv('INTERACTIONS_TOKEN')}"

    data = {
        "content": message
    }

    # Send the PATCH request
    response = requests.post(url, json=data)

    print("Response status code: ")
    print(response.status_code)
    print(response.text)