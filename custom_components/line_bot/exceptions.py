"""Exceptions for the Line Bot integration."""

from homeassistant.exceptions import HomeAssistantError


class ChatIdNotFound(HomeAssistantError):
    """When chat_id not found."""

    def __init__(self, name: str, allowed_chat_ids: dict) -> None:
        """Initialize error."""
        super().__init__(
            self,
            f"chat_id not found for '{name}', allowed names are: {list(allowed_chat_ids.keys())}",
        )
        self.name = name
        self.allowed_chat_ids = allowed_chat_ids

    def __str__(self) -> str:
        """Return string representation."""
        return f"chat_id not found for '{self.name}', allowed names are: {list(self.allowed_chat_ids.keys())}"
