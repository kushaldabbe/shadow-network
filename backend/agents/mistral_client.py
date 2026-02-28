"""Mistral API client wrapper with async helpers."""
import logging
from mistralai import Mistral
from config import MISTRAL_API_KEY, MISTRAL_MODEL

logger = logging.getLogger(__name__)

# Initialize the Mistral client
client = Mistral(api_key=MISTRAL_API_KEY)


async def chat_completion(system_prompt: str, user_message: str, temperature: float = 0.7) -> str:
    """Make an async chat completion call to Mistral API.
    
    Args:
        system_prompt: The system prompt for the agent.
        user_message: The user/order message.
        temperature: Sampling temperature (0-1).
    
    Returns:
        The assistant's response text.
    """
    try:
        response = await client.chat.complete_async(
            model=MISTRAL_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=temperature,
        )
        content = response.choices[0].message.content
        logger.info(f"Mistral response received ({len(content)} chars)")
        return content
    except Exception as e:
        logger.error(f"Mistral API error: {e}")
        raise


async def chat_completion_json(system_prompt: str, user_message: str, temperature: float = 0.5) -> str:
    """Chat completion expecting JSON output — lower temperature for reliability.
    
    Args:
        system_prompt: The system prompt.
        user_message: The user message.
        temperature: Lower default for JSON reliability.
    
    Returns:
        The assistant's response text (should be JSON).
    """
    try:
        response = await client.chat.complete_async(
            model=MISTRAL_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        logger.info(f"Mistral JSON response received ({len(content)} chars)")
        return content
    except Exception as e:
        logger.error(f"Mistral JSON API error: {e}")
        raise
