def get_message_from_response(response, idx: int = 0) -> str:
    return response.choices[idx].message.content
