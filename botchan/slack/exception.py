from slack_sdk.errors import SlackApiError


class SlackResponseError(SlackApiError):
    def __init__(self, response):
        super().__init__("Slack API request returned an error.", response=response)
        self.response = response

    def __str__(self):
        return f"{super().__str__()}\nResponse: {self.response}"
