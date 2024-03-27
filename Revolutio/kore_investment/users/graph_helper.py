from requests_oauthlib import OAuth2Session

graph_url = "https://graph.microsoft.com/v1.0"


def get_microsoft_user(token):
    graph_client = OAuth2Session(token=token)
    # Send GET to /me
    user = graph_client.get(f"{graph_url}/me")
    # Return the JSON result
    return user.json()
