from typing import Any, Type

from openai.types.chat.chat_completion import ChatCompletion

from . import OPENAI_CLIENT


def get_message_from_completion(completion: ChatCompletion, idx: int = 0) -> str:
    return completion.choices[idx].message.content


def get_parsed_choice_from_completion(completion: ChatCompletion, idx: int = 0) -> Any:
    return completion.choices[idx].message.parsed


def simple_assistant(model_id: str, prompt: str) -> str:
    completion = OPENAI_CLIENT.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": prompt},
        ],
    )
    return get_message_from_completion(completion=completion)


def simple_assistant_with_struct_ouput(
    model_id: str, prompt: str, output_schema: Type[Any]
) -> Any:
    completion = OPENAI_CLIENT.beta.chat.completions.parse(
        model=model_id,
        messages=[
            {
                "role": "system",
                "content": "Assist user with the task with structure output",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        response_format=output_schema,
    )
    return get_parsed_choice_from_completion(completion=completion)
