from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="UserCreateDTO")


@_attrs_define
class UserCreateDTO:
    """
    Attributes:
        user_id (int):
        first_name (str):
        last_name (Union[None, str]):
        username (str):
    """

    user_id: int
    first_name: str
    last_name: Union[None, str]
    username: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user_id = self.user_id

        first_name = self.first_name

        last_name: Union[None, str]
        last_name = self.last_name

        username = self.username

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "user_id": user_id,
                "first_name": first_name,
                "last_name": last_name,
                "username": username,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        user_id = d.pop("user_id")

        first_name = d.pop("first_name")

        def _parse_last_name(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        last_name = _parse_last_name(d.pop("last_name"))

        username = d.pop("username")

        user_create_dto = cls(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
        )

        user_create_dto.additional_properties = d
        return user_create_dto

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
