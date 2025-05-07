from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.generation_request_messages_item import GenerationRequestMessagesItem
    from ..models.generation_request_variables_type_0 import GenerationRequestVariablesType0


T = TypeVar("T", bound="GenerationRequest")


@_attrs_define
class GenerationRequest:
    """
    Attributes:
        messages (list['GenerationRequestMessagesItem']):
        variables (Union['GenerationRequestVariablesType0', None, Unset]):
    """

    messages: list["GenerationRequestMessagesItem"]
    variables: Union["GenerationRequestVariablesType0", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.generation_request_variables_type_0 import GenerationRequestVariablesType0

        messages = []
        for messages_item_data in self.messages:
            messages_item = messages_item_data.to_dict()
            messages.append(messages_item)

        variables: Union[None, Unset, dict[str, Any]]
        if isinstance(self.variables, Unset):
            variables = UNSET
        elif isinstance(self.variables, GenerationRequestVariablesType0):
            variables = self.variables.to_dict()
        else:
            variables = self.variables

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "messages": messages,
            }
        )
        if variables is not UNSET:
            field_dict["variables"] = variables

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.generation_request_messages_item import GenerationRequestMessagesItem
        from ..models.generation_request_variables_type_0 import GenerationRequestVariablesType0

        d = dict(src_dict)
        messages = []
        _messages = d.pop("messages")
        for messages_item_data in _messages:
            messages_item = GenerationRequestMessagesItem.from_dict(messages_item_data)

            messages.append(messages_item)

        def _parse_variables(data: object) -> Union["GenerationRequestVariablesType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                variables_type_0 = GenerationRequestVariablesType0.from_dict(data)

                return variables_type_0
            except:  # noqa: E722
                pass
            return cast(Union["GenerationRequestVariablesType0", None, Unset], data)

        variables = _parse_variables(d.pop("variables", UNSET))

        generation_request = cls(
            messages=messages,
            variables=variables,
        )

        generation_request.additional_properties = d
        return generation_request

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
