# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Iterable, List, Optional, Sequence, TypeVar, Union

from libcst._add_slots import add_slots
from libcst._maybe_sentinel import MaybeSentinel
from libcst._removal_sentinel import RemovalSentinel


if TYPE_CHECKING:
    # These are circular dependencies only used for typing purposes
    from libcst.nodes._base import CSTNode
    from libcst._base_visitor import CSTVisitor


_CSTNodeT = TypeVar("_CSTNodeT", bound="CSTNode")


@add_slots
@dataclass(frozen=False)
class CodegenState:
    # These are derived from a Module
    default_indent: str
    default_newline: str

    indent: List[str] = field(default_factory=list)
    tokens: List[str] = field(default_factory=list)


def visit_required(fieldname: str, node: _CSTNodeT, visitor: "CSTVisitor") -> _CSTNodeT:
    """
    Given a node, visits the node using `visitor`. If removal is attempted by the
    visitor, an exception is raised.
    """
    result = node.visit(visitor)
    if isinstance(result, RemovalSentinel):
        raise TypeError(
            f"We got a RemovalSentinel while visiting a {type(node).__name__}. This "
            + "node's parent does not allow it to be removed."
        )
    return result


def visit_optional(
    fieldname: str, node: Optional[_CSTNodeT], visitor: "CSTVisitor"
) -> Optional[_CSTNodeT]:
    """
    Given an optional node, visits the node if it exists with `visitor`. If the node is
    removed, returns None.
    """
    if node is None:
        return None
    result = node.visit(visitor)
    return None if isinstance(result, RemovalSentinel) else result


def visit_sentinel(
    fieldname: str, node: Union[_CSTNodeT, MaybeSentinel], visitor: "CSTVisitor"
) -> Union[_CSTNodeT, MaybeSentinel]:
    """
    Given a node that can be a real value or a sentinel value, visits the node if it
    is real with `visitor`. If the node is removed, returns MaybeSentinel.
    """
    if isinstance(node, MaybeSentinel):
        return MaybeSentinel.DEFAULT
    result = node.visit(visitor)
    return MaybeSentinel.DEFAULT if isinstance(result, RemovalSentinel) else result


def visit_iterable(
    fieldname: str, children: Iterable[_CSTNodeT], visitor: "CSTVisitor"
) -> Iterable[_CSTNodeT]:
    """
    Given an iterable of children, visits each child with `visitor`, and yields the new
    children with any `RemovalSentinel` values removed.
    """
    for child in children:
        new_child = child.visit(visitor)
        if not isinstance(new_child, RemovalSentinel):
            yield new_child


def visit_sequence(
    fieldname: str, children: Sequence[_CSTNodeT], visitor: "CSTVisitor"
) -> Sequence[_CSTNodeT]:
    """
    A convenience wrapper for `visit_iterable` that returns a sequence instead of an
    iterable.
    """
    return tuple(visit_iterable(fieldname, children, visitor))
