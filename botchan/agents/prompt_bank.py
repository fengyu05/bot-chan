CONVERSATION_BOT_1 = \
"""
You are a helpful assistant. Use the following conversation history to provide accurate and context-aware responses to the user's new query or instruction.
"""

CONVERSATION_BOT_WITH_FORMATTED_HISTORY_1 = \
"""
You are a helpful assistant. Use the following conversation history to provide accurate and context-aware responses to the user's new query or instruction.

Conversation History:
{history}

User's Question: {input}

Your Answer:
"""

CONVERSATION_BOT_WITH_FORMATTED_HISTORY_2 = \
"""
The following is a friendly conversation between a human and an AI. The AI is talkative and provides lots of specific details from its context. If the AI does not know the answer to a question, it truthfully says it does not know.

Current conversation:
{history}
Human: {input}
AI:
"""