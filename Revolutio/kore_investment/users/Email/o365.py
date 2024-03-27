from O365 import Account
from django.shortcuts import render

credentials = ("b99d0515-5aef-411a-af5f-fdab0a2d6206", "_cU62ve6R6a0~351WvI_g0wkQW9O01x3.W")
my_scopes = [
    "https://graph.microsoft.com/offline_access",
    "https://graph.microsoft.com/User.Read",
    "https://graph.microsoft.com/Mail.ReadWrite",
    "https://graph.microsoft.com/Mail.Send",
]


def auth_step_one(request):

    account = Account(
        credentials, auth_flow_type="credentials", tenant_id="4bf6db98-c05a-4a1e-ac6a-340dcfa47097"
    )
    if account.authenticate():
        m = account.mailbox(resource="srijanraychaudhuri@acies.consulting")
        m = account.new_message(resource="srijanraychaudhuri@acies.consulting")
        m.to.add("muzammilpatel@acies.consulting")
        m.subject = "Testing!"
        m.body = "Testing mails from Revolutio. Need to discuss this in the morning. Will call at 10 AM"
        m.send()
    data = {}
    data["Status"] = "Success"
    return render(request, "api_integration.html", data)


def auth_step_two_callback(request):
    account = Account(credentials)

    # retreive the state saved in auth_step_one
    my_saved_state = get_state(request)  # example...

    # rebuild the redirect_uri used in auth_step_one
    callback = "http://localhost:8000/users/o365login_step2/"

    result = account.con.request_token(request.url, state=my_saved_state, redirect_uri=callback)
    # if result is True, then authentication was succesful
    #  and the auth token is stored in the token backend
    if result:
        data = {}
        data["Status"] = "Success"
        return render(request, "api_integration.html", data)
    # else ....


def store_state(request, state):
    request.session["o365_state"] = state


def get_state(request):
    state = request.session["o365_state"]
    return state
