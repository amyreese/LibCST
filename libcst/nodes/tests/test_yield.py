# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict
from typing import Callable

import libcst.nodes as cst
from libcst.nodes.tests.base import CSTNodeTest
from libcst.parser import parse_statement
from libcst.testing.utils import data_provider


class YieldConstructionTest(CSTNodeTest):
    @data_provider(
        (
            # Simple yield
            (cst.Yield(), "yield"),
            # yield expression
            (cst.Yield(cst.Name("a")), "yield a"),
            # yield from expression
            (cst.Yield(cst.From(cst.Call(cst.Name("a")))), "yield from a()"),
            # Parenthesizing tests
            (
                cst.Yield(
                    lpar=(cst.LeftParen(),),
                    value=cst.Number(cst.Integer("5")),
                    rpar=(cst.RightParen(),),
                ),
                "(yield 5)",
            ),
            # Whitespace oddities tests
            (
                cst.Yield(
                    cst.Name("a", lpar=(cst.LeftParen(),), rpar=(cst.RightParen(),)),
                    whitespace_after_yield=cst.SimpleWhitespace(""),
                ),
                "yield(a)",
            ),
            (
                cst.Yield(
                    cst.From(
                        cst.Call(
                            cst.Name("a"),
                            lpar=(cst.LeftParen(),),
                            rpar=(cst.RightParen(),),
                        ),
                        whitespace_after_from=cst.SimpleWhitespace(""),
                    )
                ),
                "yield from(a())",
            ),
            # Whitespace rendering/parsing tests
            (
                cst.Yield(
                    lpar=(cst.LeftParen(whitespace_after=cst.SimpleWhitespace(" ")),),
                    value=cst.Number(cst.Integer("5")),
                    whitespace_after_yield=cst.SimpleWhitespace("  "),
                    rpar=(cst.RightParen(whitespace_before=cst.SimpleWhitespace(" ")),),
                ),
                "( yield  5 )",
            ),
            (
                cst.Yield(
                    lpar=(cst.LeftParen(whitespace_after=cst.SimpleWhitespace(" ")),),
                    value=cst.From(
                        cst.Call(cst.Name("bla")),
                        whitespace_after_from=cst.SimpleWhitespace("  "),
                    ),
                    whitespace_after_yield=cst.SimpleWhitespace("  "),
                    rpar=(cst.RightParen(whitespace_before=cst.SimpleWhitespace(" ")),),
                ),
                "( yield  from  bla() )",
            ),
        )
    )
    def test_valid(self, node: cst.CSTNode, code: str) -> None:
        self.validate_node(node, code)

    @data_provider(
        (
            # Paren validation
            (
                lambda: cst.Yield(lpar=(cst.LeftParen(),)),
                "left paren without right paren",
            ),
            (
                lambda: cst.Yield(rpar=(cst.RightParen(),)),
                "right paren without left paren",
            ),
            # Make sure we have adequate space after yield
            (
                lambda: cst.Yield(
                    cst.Name("a"), whitespace_after_yield=cst.SimpleWhitespace("")
                ),
                "Must have at least one space after 'yield' keyword",
            ),
            (
                lambda: cst.Yield(
                    cst.From(cst.Call(cst.Name("a"))),
                    whitespace_after_yield=cst.SimpleWhitespace(""),
                ),
                "Must have at least one space after 'yield' keyword",
            ),
            # MAke sure we have adequate space after from
            (
                lambda: cst.Yield(
                    cst.From(
                        cst.Call(cst.Name("a")),
                        whitespace_after_from=cst.SimpleWhitespace(""),
                    )
                ),
                "Must have at least one space after 'from' keyword",
            ),
        )
    )
    def test_invalid(
        self, get_node: Callable[[], cst.CSTNode], expected_re: str
    ) -> None:
        self.assert_invalid(get_node, expected_re)


class YieldParsingTest(CSTNodeTest):
    @data_provider(
        (
            # Simple yield
            (cst.Yield(), "yield"),
            # yield expression
            (
                cst.Yield(
                    cst.Name("a"), whitespace_after_yield=cst.SimpleWhitespace(" ")
                ),
                "yield a",
            ),
            # yield from expression
            (
                cst.Yield(
                    cst.From(
                        cst.Call(cst.Name("a")),
                        whitespace_after_from=cst.SimpleWhitespace(" "),
                    ),
                    whitespace_after_yield=cst.SimpleWhitespace(" "),
                ),
                "yield from a()",
            ),
            # Parenthesizing tests
            (
                cst.Yield(
                    lpar=(cst.LeftParen(),),
                    whitespace_after_yield=cst.SimpleWhitespace(" "),
                    value=cst.Number(cst.Integer("5")),
                    rpar=(cst.RightParen(),),
                ),
                "(yield 5)",
            ),
            # Whitespace oddities tests
            (
                cst.Yield(
                    cst.Name("a", lpar=(cst.LeftParen(),), rpar=(cst.RightParen(),)),
                    whitespace_after_yield=cst.SimpleWhitespace(""),
                ),
                "yield(a)",
            ),
            (
                cst.Yield(
                    cst.From(
                        cst.Call(
                            cst.Name("a"),
                            lpar=(cst.LeftParen(),),
                            rpar=(cst.RightParen(),),
                        ),
                        whitespace_after_from=cst.SimpleWhitespace(""),
                    ),
                    whitespace_after_yield=cst.SimpleWhitespace(" "),
                ),
                "yield from(a())",
            ),
            # Whitespace rendering/parsing tests
            (
                cst.Yield(
                    lpar=(cst.LeftParen(whitespace_after=cst.SimpleWhitespace(" ")),),
                    value=cst.Number(cst.Integer("5")),
                    whitespace_after_yield=cst.SimpleWhitespace("  "),
                    rpar=(cst.RightParen(whitespace_before=cst.SimpleWhitespace(" ")),),
                ),
                "( yield  5 )",
            ),
            (
                cst.Yield(
                    lpar=(cst.LeftParen(whitespace_after=cst.SimpleWhitespace(" ")),),
                    value=cst.From(
                        cst.Call(cst.Name("bla")),
                        whitespace_after_from=cst.SimpleWhitespace("  "),
                    ),
                    whitespace_after_yield=cst.SimpleWhitespace("  "),
                    rpar=(cst.RightParen(whitespace_before=cst.SimpleWhitespace(" ")),),
                ),
                "( yield  from  bla() )",
            ),
        )
    )
    def test_valid(self, node: cst.CSTNode, code: str) -> None:
        # pyre-fixme[16]: `BaseSuite` has no attribute `__getitem__`.
        self.validate_node(node, code, lambda code: parse_statement(code).body[0].value)
