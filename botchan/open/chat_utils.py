from . import OPENAI_CLIENT


def get_message_from_response(response, idx: int = 0) -> str:
    return response.choices[idx].message.content


def simple_assistant(model_id: str, prompt: str) -> str:
    response = OPENAI_CLIENT.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": prompt},
        ],
    )
    return get_message_from_response(response=response)
