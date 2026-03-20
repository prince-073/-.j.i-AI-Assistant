"""
API KEY ROTATION
================

Ensures the brain (classification) and chat (main LLM) never use the same
Groq API key for a single request. Keys rotate in order: 1, 2, 3, 4, 5...

HOW IT WORKS:
  For each request, we assign:
    - brain_key_index: used by the classification model
    - chat_key_index: used by the main chat/response model

  They are always different (brain uses key i, chat uses key i+1).
  Across requests, we cycle through all keys evenly.

EXAMPLE (5 keys: 0,1,2,3,4):
  Request 1: brain=0, chat=1
  Request 2: brain=2, chat=3
  Request 3: brain=4, chat=0
  Request 4: brain=1, chat=2
  Request 5: brain=3, chat=4
  ...

For non-Jarvis (general/realtime without brain): only chat is used.
  Request: chat=0
  Request: chat=1
  ...
"""

import threading
from typing import Tuple, Optional

_counter = 0
_lock = threading.Lock()


def get_next_key_pair(n_keys: int, need_brain: bool = True) -> Tuple[Optional[int], int]:
    """
    Get the next (brain_key_index, chat_key_index) for a request.

    Args:
        n_keys: Total number of Groq API keys.
        need_brain: True for Jarvis (brain + chat), False for general/realtime (chat only).

    Returns:
        (brain_key_index, chat_key_index) for need_brain=True.
        (None, chat_key_index) for need_brain=False.
    """
    global _counter
    if n_keys <= 0:
        return (None, 0)
    with _lock:
        if need_brain:
            if n_keys >= 2:
                brain = _counter % n_keys
                chat = (_counter + 1) % n_keys
                _counter += 2
                return (brain, chat)
            else:
                # Single key: brain and chat both use key 0 (no choice)
                _counter += 1
                return (0, 0)
        else:
            chat = _counter % n_keys
            _counter += 1
            return (None, chat)
