from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class UserProfile:
    title: str
    phone: str
    skype: str
    real_name: str
    real_name_normalized: str
    display_name: str
    display_name_normalized: str
    fields: Dict[str, Any]
    status_text: str
    status_emoji: str
    status_emoji_display_info: List[Dict[str, Any]]
    status_expiration: int
    avatar_hash: str
    image_original: str
    is_custom_image: bool
    email: str
    first_name: str
    last_name: str
    image_24: str
    image_32: str
    image_48: str
    image_72: str
    image_192: str
    image_512: str
    image_1024: str
    status_text_canonical: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserProfile":
        fields = {}
        for key, value in data.get("fields", {}).items():
            fields[key] = value.get("value")

        return cls(
            title=data.get("title", ""),
            phone=data.get("phone", ""),
            skype=data.get("skype", ""),
            real_name=data.get("real_name", ""),
            real_name_normalized=data.get("real_name_normalized", ""),
            display_name=data.get("display_name", ""),
            display_name_normalized=data.get("display_name_normalized", ""),
            fields=fields,
            status_text=data.get("status_text", ""),
            status_emoji=data.get("status_emoji", ""),
            status_emoji_display_info=data.get("status_emoji_display_info", []),
            status_expiration=data.get("status_expiration", 0),
            avatar_hash=data.get("avatar_hash", ""),
            image_original=data.get("image_original", ""),
            is_custom_image=data.get("is_custom_image", False),
            email=data.get("email", ""),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            image_24=data.get("image_24", ""),
            image_32=data.get("image_32", ""),
            image_48=data.get("image_48", ""),
            image_72=data.get("image_72", ""),
            image_192=data.get("image_192", ""),
            image_512=data.get("image_512", ""),
            image_1024=data.get("image_1024", ""),
            status_text_canonical=data.get("status_text_canonical", ""),
        )
