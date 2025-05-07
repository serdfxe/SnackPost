from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.generation_response_usage import GenerationResponseUsage


T = TypeVar("T", bound="GenerationResponse")


@_attrs_define
class GenerationResponse:
    """
    Attributes:
        content (str):
        usage (GenerationResponseUsage):
    """

    content: str
    usage: "GenerationResponseUsage"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        content = self.content

        usage = self.usage.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "content": content,
                "usage": usage,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.generation_response_usage import GenerationResponseUsage

        d = dict(src_dict)
        content = d.pop("content")

        usage = GenerationResponseUsage.from_dict(d.pop("usage"))

        generation_response = cls(
            content=content,
            usage=usage,
        )

        generation_response.additional_properties = d
        return generation_response

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
