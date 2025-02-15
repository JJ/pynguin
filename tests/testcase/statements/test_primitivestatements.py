#  This file is part of Pynguin.
#
#  SPDX-FileCopyrightText: 2019–2021 Pynguin Contributors
#
#  SPDX-License-Identifier: LGPL-3.0-or-later
#
from unittest import mock
from unittest.mock import MagicMock

import pytest

import pynguin.configuration as config
import pynguin.testcase.defaulttestcase as dtc
import pynguin.testcase.statements.primitivestatements as prim
import pynguin.testcase.testcase as tc
import pynguin.testcase.variable.variablereferenceimpl as vri


@pytest.mark.parametrize(
    "statement_type,value",
    [
        pytest.param(prim.IntPrimitiveStatement, 42),
        pytest.param(prim.FloatPrimitiveStatement, 42.23),
        pytest.param(prim.StringPrimitiveStatement, "foo"),
        pytest.param(prim.BytesPrimitiveStatement, b"test"),
        pytest.param(prim.BooleanPrimitiveStatement, True),
    ],
)
def test_primitive_statement_value(statement_type, test_case_mock, value):
    statement = statement_type(test_case_mock, value)
    assert statement.value == value


@pytest.mark.parametrize(
    "statement_type",
    [
        pytest.param(prim.IntPrimitiveStatement),
        pytest.param(prim.FloatPrimitiveStatement),
        pytest.param(prim.StringPrimitiveStatement),
        pytest.param(prim.BytesPrimitiveStatement),
        pytest.param(prim.BooleanPrimitiveStatement),
    ],
)
def test_primitive_statement_value_none(statement_type, test_case_mock):
    statement = statement_type(test_case_mock, None)
    assert statement.value is not None


@pytest.mark.parametrize(
    "statement_type,value,new_value",
    [
        pytest.param(prim.IntPrimitiveStatement, 42, 23),
        pytest.param(prim.FloatPrimitiveStatement, 2.1, 1.2),
        pytest.param(prim.StringPrimitiveStatement, "foo", "bar"),
        pytest.param(prim.BytesPrimitiveStatement, b"foo", b"bar"),
        pytest.param(prim.BooleanPrimitiveStatement, True, False),
    ],
)
def test_primitive_statement_set_value(
    statement_type, test_case_mock, value, new_value
):
    statement = statement_type(test_case_mock, value)
    statement.value = new_value
    assert statement.value == new_value


@pytest.mark.parametrize(
    "statement_type,test_case,new_test_case,value",
    [
        pytest.param(
            prim.IntPrimitiveStatement,
            MagicMock(tc.TestCase),
            MagicMock(tc.TestCase),
            42,
        ),
        pytest.param(
            prim.FloatPrimitiveStatement,
            MagicMock(tc.TestCase),
            MagicMock(tc.TestCase),
            42.23,
        ),
        pytest.param(
            prim.StringPrimitiveStatement,
            MagicMock(tc.TestCase),
            MagicMock(tc.TestCase),
            "foo",
        ),
        pytest.param(
            prim.BytesPrimitiveStatement,
            MagicMock(tc.TestCase),
            MagicMock(tc.TestCase),
            b"foo",
        ),
        pytest.param(
            prim.BooleanPrimitiveStatement,
            MagicMock(tc.TestCase),
            MagicMock(tc.TestCase),
            True,
        ),
    ],
)
def test_primitive_statement_clone(statement_type, test_case, new_test_case, value):
    statement = statement_type(test_case, value)
    new_statement = statement.clone(new_test_case)
    assert new_statement.test_case == new_test_case
    assert new_statement.ret_val.variable_type == statement.ret_val.variable_type
    assert new_statement.value == statement.value


@pytest.mark.parametrize(
    "statement_type,test_case,value,visitor_method",
    [
        pytest.param(
            prim.IntPrimitiveStatement,
            MagicMock(tc.TestCase),
            42,
            "visit_int_primitive_statement",
        ),
        pytest.param(
            prim.FloatPrimitiveStatement,
            MagicMock(tc.TestCase),
            2.1,
            "visit_float_primitive_statement",
        ),
        pytest.param(
            prim.StringPrimitiveStatement,
            MagicMock(tc.TestCase),
            "foo",
            "visit_string_primitive_statement",
        ),
        pytest.param(
            prim.BytesPrimitiveStatement,
            MagicMock(tc.TestCase),
            b"foo",
            "visit_bytes_primitive_statement",
        ),
        pytest.param(
            prim.BooleanPrimitiveStatement,
            MagicMock(tc.TestCase),
            True,
            "visit_boolean_primitive_statement",
        ),
    ],
)
def test_primitive_statement_accept(statement_type, test_case, value, visitor_method):
    stmt = statement_type(test_case, value)
    visitor = MagicMock()
    stmt.accept(visitor)
    getattr(visitor, visitor_method).assert_called_once_with(stmt)


@pytest.mark.parametrize(
    "statement_type,value",
    [
        pytest.param(prim.IntPrimitiveStatement, 42),
        pytest.param(prim.FloatPrimitiveStatement, 42.23),
        pytest.param(prim.StringPrimitiveStatement, "foo"),
        pytest.param(prim.BytesPrimitiveStatement, b"foo"),
        pytest.param(prim.BooleanPrimitiveStatement, True),
    ],
)
def test_primitive_statement_equals_same(statement_type, value):
    test_case = MagicMock(tc.TestCase)
    statement = statement_type(test_case, value)
    assert statement.__eq__(statement)


@pytest.mark.parametrize(
    "statement_type,value",
    [
        pytest.param(prim.IntPrimitiveStatement, 42),
        pytest.param(prim.FloatPrimitiveStatement, 42.23),
        pytest.param(prim.StringPrimitiveStatement, "foo"),
        pytest.param(prim.BytesPrimitiveStatement, b"foo"),
        pytest.param(prim.BooleanPrimitiveStatement, True),
    ],
)
def test_primitive_statement_equals_other_type(statement_type, value):
    test_case = MagicMock(tc.TestCase)
    statement = statement_type(test_case, value)
    assert not statement.__eq__(test_case)


@pytest.mark.parametrize(
    "statement_type,value",
    [
        pytest.param(prim.IntPrimitiveStatement, 42),
        pytest.param(prim.FloatPrimitiveStatement, 42.23),
        pytest.param(prim.StringPrimitiveStatement, "foo"),
        pytest.param(prim.BytesPrimitiveStatement, b"foo"),
        pytest.param(prim.BooleanPrimitiveStatement, True),
    ],
)
def test_primitive_statement_equals_clone(statement_type, value):
    test_case = MagicMock(tc.TestCase)
    statement = statement_type(test_case, value)
    test_case.statements = [statement]
    test_case2 = MagicMock(tc.TestCase)
    clone = statement.clone(test_case2)
    test_case2.statements = [clone]
    assert statement.__eq__(clone)


def test_none_statement_equals_clone():
    test_case = MagicMock(tc.TestCase)
    statement = prim.NoneStatement(test_case, type(None))
    test_case.statements = [statement]
    test_case2 = MagicMock(tc.TestCase)
    clone = statement.clone(test_case2)
    test_case2.statements = [clone]
    assert statement.__eq__(clone)


@pytest.mark.parametrize(
    "statement_type,value",
    [
        pytest.param(prim.IntPrimitiveStatement, 42),
        pytest.param(prim.FloatPrimitiveStatement, 42.23),
        pytest.param(prim.StringPrimitiveStatement, "foo"),
        pytest.param(prim.BytesPrimitiveStatement, b"foo"),
        pytest.param(prim.BooleanPrimitiveStatement, True),
    ],
)
def test_primitive_statement_hash(statement_type, value):
    statement = statement_type(MagicMock(tc.TestCase), value)
    assert statement.__hash__() != 0


def test_int_primitive_statement_randomize_value(test_case_mock):
    statement = prim.IntPrimitiveStatement(test_case_mock)
    statement.randomize_value()
    assert isinstance(statement.value, int)


def test_float_primitive_statement_randomize_value(test_case_mock):
    statement = prim.FloatPrimitiveStatement(test_case_mock)
    statement.randomize_value()
    assert isinstance(statement.value, float)


def test_bool_primitive_statement_randomize_value(test_case_mock):
    statement = prim.BooleanPrimitiveStatement(test_case_mock)
    statement.randomize_value()
    assert statement.value or not statement.value


def test_string_primitive_statement_randomize_value(test_case_mock):
    statement = prim.StringPrimitiveStatement(test_case_mock)
    statement.randomize_value()
    assert 0 <= len(statement.value) <= config.configuration.test_creation.string_length


def test_bytes_primitive_statement_randomize_value(test_case_mock):
    statement = prim.BytesPrimitiveStatement(test_case_mock)
    statement.randomize_value()
    assert 0 <= len(statement.value) <= config.configuration.test_creation.bytes_length
    assert isinstance(statement.value, bytes)


def test_none_statement_randomize_value(test_case_mock):
    statement = prim.NoneStatement(test_case_mock, type(None))
    statement.randomize_value()
    assert statement.value is None


def test_none_statement_delta(test_case_mock):
    statement = prim.NoneStatement(test_case_mock, type(None))
    statement.delta()
    assert statement.value is None


def test_string_primitive_statement_random_deletion(test_case_mock):
    sample = list("Test")
    result = prim.StringPrimitiveStatement._random_deletion(sample)
    assert len(result) <= len(sample)


def test_string_primitive_statement_random_insertion(test_case_mock):
    sample = list("Test")
    result = prim.StringPrimitiveStatement._random_insertion(sample)
    assert len(result) >= len(sample)


def test_string_primitive_statement_random_insertion_empty(test_case_mock):
    sample = list("")
    result = prim.StringPrimitiveStatement._random_insertion(sample)
    assert len(result) >= len(sample)


def test_string_primitive_statement_random_replacement(test_case_mock):
    sample = list("Test")
    result = prim.StringPrimitiveStatement._random_replacement(sample)
    assert len(result) == len(sample)


def test_string_primitive_statement_delta_none(test_case_mock):
    value = "t"
    statement = prim.StringPrimitiveStatement(test_case_mock, value)
    with mock.patch("pynguin.utils.randomness.next_float") as float_mock:
        float_mock.side_effect = [1.0, 1.0, 1.0]
        statement.delta()
        assert statement.value == value


def test_string_primitive_statement_delta_all(test_case_mock):
    value = "te"
    statement = prim.StringPrimitiveStatement(test_case_mock, value)
    with mock.patch("pynguin.utils.randomness.next_char") as char_mock:
        char_mock.side_effect = ["a", "b"]
        with mock.patch("pynguin.utils.randomness.next_int") as int_mock:
            int_mock.return_value = 0
            with mock.patch("pynguin.utils.randomness.next_float") as float_mock:
                deletion = [0.0, 0.0, 1.0]
                replacement = [0.0, 0.0]
                insertion = [0.0, 0.0, 1.0]
                float_mock.side_effect = deletion + replacement + insertion
                statement.delta()
                assert statement.value == "ba"


def test_bytes_primitive_statement_random_deletion(test_case_mock):
    sample = list(b"Test")
    result = prim.BytesPrimitiveStatement._random_deletion(sample)
    assert len(result) <= len(sample)


def test_bytes_primitive_statement_random_insertion(test_case_mock):
    sample = list(b"Test")
    result = prim.BytesPrimitiveStatement._random_insertion(sample)
    assert len(result) >= len(sample)


def test_bytes_primitive_statement_random_insertion_empty(test_case_mock):
    sample = list(b"")
    result = prim.BytesPrimitiveStatement._random_insertion(sample)
    assert len(result) >= len(sample)


def test_bytes_primitive_statement_random_replacement(test_case_mock):
    sample = list(b"Test")
    result = prim.BytesPrimitiveStatement._random_replacement(sample)
    assert len(result) == len(sample)


def test_bytes_primitive_statement_delta_none(test_case_mock):
    value = b"t"
    statement = prim.BytesPrimitiveStatement(test_case_mock, value)
    with mock.patch("pynguin.utils.randomness.next_float") as float_mock:
        float_mock.side_effect = [1.0, 1.0, 1.0]
        statement.delta()
        assert statement.value == value


def test_bytes_primitive_statement_delta_all(test_case_mock):
    value = b"te"
    statement = prim.BytesPrimitiveStatement(test_case_mock, value)
    with mock.patch("pynguin.utils.randomness.next_byte") as char_mock:
        char_mock.side_effect = [12, 128]
        with mock.patch("pynguin.utils.randomness.next_int") as int_mock:
            int_mock.return_value = 0
            with mock.patch("pynguin.utils.randomness.next_float") as float_mock:
                deletion = [0.0, 0.0, 1.0]
                replacement = [0.0, 0.0]
                insertion = [0.0, 0.0, 1.0]
                float_mock.side_effect = deletion + replacement + insertion
                statement.delta()
                assert statement.value == b"\x80\x0c"


def test_int_primitive_statement_delta(test_case_mock):
    config.configuration.test_creation.max_delta = 10
    statement = prim.IntPrimitiveStatement(test_case_mock, 1)
    with mock.patch("pynguin.utils.randomness.next_gaussian") as gauss_mock:
        gauss_mock.return_value = 0.5
        statement.delta()
    assert statement.value == 6


def test_float_primitive_statement_delta_max(test_case_mock):
    config.configuration.test_creation.max_delta = 10
    statement = prim.FloatPrimitiveStatement(test_case_mock, 1.5)
    with mock.patch("pynguin.utils.randomness.next_gaussian") as gauss_mock:
        gauss_mock.return_value = 0.5
        with mock.patch("pynguin.utils.randomness.next_float") as float_mock:
            float_mock.return_value = 0.0
            statement.delta()
            assert statement.value == 6.5


def test_float_primitive_statement_delta_gauss(test_case_mock):
    config.configuration.test_creation.max_delta = 10
    statement = prim.FloatPrimitiveStatement(test_case_mock, 1.0)
    with mock.patch("pynguin.utils.randomness.next_gaussian") as gauss_mock:
        gauss_mock.return_value = 0.5
        with mock.patch("pynguin.utils.randomness.next_float") as float_mock:
            float_mock.return_value = 1.0 / 3.0
            statement.delta()
            assert statement.value == 1.5


def test_float_primitive_statement_delta_round(test_case_mock):
    statement = prim.FloatPrimitiveStatement(test_case_mock, 1.2345)
    with mock.patch("pynguin.utils.randomness.next_int") as int_mock:
        int_mock.return_value = 2
        with mock.patch("pynguin.utils.randomness.next_float") as float_mock:
            float_mock.return_value = 2.0 / 3.0
            statement.delta()
            assert statement.value == 1.23


def test_boolean_primitive_statement_delta(test_case_mock):
    statement = prim.BooleanPrimitiveStatement(test_case_mock, True)
    statement.delta()
    assert not statement.value


def test_primitive_statement_mutate_delta(test_case_mock):
    statement = prim.IntPrimitiveStatement(test_case_mock, 2)
    with mock.patch("pynguin.utils.randomness.next_float") as float_mock:
        float_mock.return_value = 1.0
        with mock.patch.object(statement, "delta") as rnd_mock:

            def mock_rnd():
                statement._value = 42

            rnd_mock.side_effect = mock_rnd
            statement.mutate()
            rnd_mock.assert_called_once()
            assert statement.value == 42


def test_primitive_statement_mutate_constant(test_case_mock):
    statement = prim.IntPrimitiveStatement(test_case_mock, 2)
    with mock.patch("pynguin.utils.randomness.next_float") as float_mock:
        float_mock.return_value = 0.0
        with mock.patch.object(statement, "randomize_value") as rnd_mock:

            def mock_rnd():
                statement._value = 42

            rnd_mock.side_effect = mock_rnd
            statement.mutate()
            rnd_mock.assert_called_once()
            assert statement.value == 42


def test_primitive_statement_accessible(test_case_mock):
    statement = prim.IntPrimitiveStatement(test_case_mock, 0)
    assert statement.accessible_object() is None


def test_primitive_statement_references(test_case_mock):
    statement = prim.IntPrimitiveStatement(test_case_mock, 0)
    assert {statement.ret_val} == statement.get_variable_references()


def test_primitive_statement_replace(test_case_mock):
    statement = prim.IntPrimitiveStatement(test_case_mock, 0)
    new = vri.VariableReferenceImpl(test_case_mock, int)
    statement.replace(statement.ret_val, new)
    assert statement.ret_val == new


def test_primitive_statement_replace_ignore(test_case_mock):
    statement = prim.IntPrimitiveStatement(test_case_mock, 0)
    new = prim.FloatPrimitiveStatement(test_case_mock, 0).ret_val
    old = statement.ret_val
    statement.replace(new, new)
    assert statement.ret_val == old


def test_primitive_statement_get_position():
    test_case = dtc.DefaultTestCase()
    statement = prim.IntPrimitiveStatement(test_case, 5)
    test_case.add_statement(statement)
    assert statement.get_position() == 0
