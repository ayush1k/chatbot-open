from openai import OpenAI
from utils.parser import format_project_context

def get_openai_client(api_key: str) -> OpenAI:
    """
    Initializes and returns the OpenAI client pointing to OpenRouter.
    """
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

def assemble_payload(developer_mode: str, dev_modes_dict: dict, readme_context: str, chat_summary: str, messages: list) -> list:
    """
    Assembles the final API payload including System prompt (Developer Mode instruction, 
    formatted context instructions, conversation summary) and the message history.
    """
    system_parts = []
    
    # Prepend Developer Mode persona instructions
    persona_instruction = dev_modes_dict.get(developer_mode, dev_modes_dict.get("Default Assistant", ""))
    if persona_instruction:
        system_parts.append(persona_instruction)
        
    # Append project context (formatted via utils.parser)
    formatted_context = format_project_context(readme_context)
    if formatted_context:
        system_parts.append(formatted_context)
        
    # Append conversation summary if it exists
    if chat_summary:
        system_parts.append(f"Summary of previous conversation:\n{chat_summary}")
        
    system_instruction = "\n\n".join(system_parts)
    
    payload = [{"role": "system", "content": system_instruction}]
    payload.extend(messages)
    return payload

def stream_chat_completion(client, model_id: str, payload: list):
    """
    Calls the OpenAI client to create a streaming chat completion.
    Yields chunks of the response content as they arrive.
    """
    stream = client.chat.completions.create(
        model=model_id,
        messages=payload,
        stream=True,
    )
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content
