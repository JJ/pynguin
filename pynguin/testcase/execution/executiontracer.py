#  This file is part of Pynguin.
#
#  SPDX-FileCopyrightText: 2019–2021 Pynguin Contributors
#
#  SPDX-License-Identifier: LGPL-3.0-or-later
#
"""Provides capabilities to track branch distances."""
import dataclasses
import logging
import threading
from math import inf
from types import CodeType
from typing import Any, Callable, Dict, Optional, Set, Tuple

from bytecode import Compare
from jellyfish import levenshtein_distance

from pynguin.analyses.controlflow.cfg import CFG
from pynguin.analyses.controlflow.controldependencegraph import ControlDependenceGraph
from pynguin.testcase.execution.executiontrace import ExecutionTrace
from pynguin.utils.type_utils import (
    given_exception_matches,
    is_bytes,
    is_numeric,
    is_string,
)


@dataclasses.dataclass
class CodeObjectMetaData:
    """Stores meta data of a code object."""

    # The raw code object.
    code_object: CodeType

    # Id of the parent code object, if any
    parent_code_object_id: Optional[int]

    # CFG of this Code Object
    cfg: CFG

    # CDG of this Code Object
    cdg: ControlDependenceGraph


@dataclasses.dataclass
class PredicateMetaData:
    """Stores meta data of a predicate."""

    # Line number where the predicate is defined.
    line_no: Optional[int]

    # Id of the code object where the predicate was defined.
    code_object_id: int


@dataclasses.dataclass
class KnownData:
    """Contains known code objects and predicates.
    FIXME(fk) better class name...
    """

    # Maps all known ids of Code Objects to meta information
    existing_code_objects: Dict[int, CodeObjectMetaData] = dataclasses.field(
        default_factory=dict
    )

    # Stores which of the existing code objects do not contain a branch, i.e.,
    # they do not contain a predicate. Every code object is initially seen as
    # branch-less until a predicate is registered for it.
    branch_less_code_objects: Set[int] = dataclasses.field(default_factory=set)

    # Maps all known ids of predicates to meta information
    existing_predicates: Dict[int, PredicateMetaData] = dataclasses.field(
        default_factory=dict
    )


class ExecutionTracer:
    """Tracks branch distances during execution.
    The results are stored in an execution trace."""

    _logger = logging.getLogger(__name__)

    # Contains static information about how branch distances
    # for certain op codes should be computed.
    # The returned tuple for each computation is (true distance, false distance).
    # pylint: disable=arguments-out-of-order
    _DISTANCE_COMPUTATIONS: Dict[Compare, Callable[[Any, Any], Tuple[float, float]]] = {
        Compare.EQ: lambda val1, val2: (
            _eq(val1, val2),
            _neq(val1, val2),
        ),
        Compare.NE: lambda val1, val2: (
            _neq(val1, val2),
            _eq(val1, val2),
        ),
        Compare.LT: lambda val1, val2: (
            _lt(val1, val2),
            _le(val2, val1),
        ),
        Compare.LE: lambda val1, val2: (
            _le(val1, val2),
            _lt(val2, val1),
        ),
        Compare.GT: lambda val1, val2: (
            _lt(val2, val1),
            _le(val1, val2),
        ),
        Compare.GE: lambda val1, val2: (
            _le(val2, val1),
            _lt(val1, val2),
        ),
        Compare.IN: lambda val1, val2: (
            _in(val1, val2),
            _nin(val1, val2),
        ),
        Compare.NOT_IN: lambda val1, val2: (
            _nin(val1, val2),
            _in(val1, val2),
        ),
        Compare.IS: lambda val1, val2: (
            _is(val1, val2),
            _isn(val1, val2),
        ),
        Compare.IS_NOT: lambda val1, val2: (
            _isn(val1, val2),
            _is(val1, val2),
        ),
    }

    def __init__(self) -> None:
        self._known_data = KnownData()
        # Contains the trace information that is generated when a module is imported
        self._import_trace = ExecutionTrace()
        self._init_trace()
        self._enabled = True
        self._current_thread_ident: Optional[int] = None

    @property
    def current_thread_ident(self) -> Optional[int]:
        """Get the current thread ident."""
        return self._current_thread_ident

    @current_thread_ident.setter
    def current_thread_ident(self, current: int) -> None:
        """Set the current thread ident. Tracing calls from any other thread
        are ignored.

        Args:
            current: the current thread
        """
        self._current_thread_ident = current

    @property
    def import_trace(self) -> ExecutionTrace:
        """The trace that was generated when the SUT was imported."""
        copied = ExecutionTrace()
        copied.merge(self._import_trace)
        return copied

    def get_known_data(self) -> KnownData:
        """Provide known data.

        Returns:
            The known data about the execution
        """
        return self._known_data

    def reset(self) -> None:
        """Resets everything.

        Should be called before instrumentation. Clears all data, so we can handle a
        reload of the SUT.
        """
        self._known_data = KnownData()
        self._import_trace = ExecutionTrace()
        self._init_trace()

    def store_import_trace(self) -> None:
        """Stores the current trace as the import trace.

        Should only be done once, after a module was loaded. The import trace will be
        merged into every subsequently recorded trace.
        """
        self._import_trace = self._trace
        self._init_trace()

    def _init_trace(self) -> None:
        """Create a new trace that only contains the trace data from the import."""
        new_trace = ExecutionTrace()
        new_trace.merge(self._import_trace)
        self._trace = new_trace

    def _is_disabled(self) -> bool:
        """Should we track anything?

        We might have to disable tracing, e.g. when calling __eq__ ourselves.
        Otherwise we create an endless recursion.

        Returns:
            Whether or not we should track anything
        """
        return not self._enabled

    def enable(self) -> None:
        """Enable tracing."""
        self._enabled = True

    def disable(self) -> None:
        """Disable tracing."""
        self._enabled = False

    def get_trace(self) -> ExecutionTrace:
        """Get the trace with the current information.

        Returns:
            The current execution trace
        """
        return self._trace

    def clear_trace(self) -> None:
        """Clear trace."""
        self._init_trace()

    def register_code_object(self, meta: CodeObjectMetaData) -> int:
        """Declare that a code object exists.

        Args:
            meta: the code objects existing

        Returns:
            the id of the code object, which can be used to identify the object
            during instrumentation.
        """
        code_object_id = len(self._known_data.existing_code_objects)
        self._known_data.existing_code_objects[code_object_id] = meta
        self._known_data.branch_less_code_objects.add(code_object_id)
        return code_object_id

    def executed_code_object(self, code_object_id: int) -> None:
        """Mark a code object as executed.

        This means, that the routine which refers to this code object was at least
        called once.

        Args:
            code_object_id: the code object id to mark
        """
        if threading.currentThread().ident != self._current_thread_ident:
            return

        assert (
            code_object_id in self._known_data.existing_code_objects
        ), "Cannot trace unknown code object"
        self._trace.executed_code_objects.add(code_object_id)

    def register_predicate(self, meta: PredicateMetaData) -> int:
        """Declare that a predicate exists.

        Args:
            meta: Meta data about the predicates

        Returns:
            the id of the predicate, which can be used to identify the predicate
            during instrumentation.
        """
        predicate_id = len(self._known_data.existing_predicates)
        self._known_data.existing_predicates[predicate_id] = meta
        self._known_data.branch_less_code_objects.discard(meta.code_object_id)
        return predicate_id

    def executed_compare_predicate(
        self, value1, value2, predicate: int, cmp_op: Compare
    ) -> None:
        """A predicate that is based on a comparison was executed.

        Args:
            value1: the first value
            value2: the second value
            predicate: the predicate identifier
            cmp_op: the compare operation
        """
        if threading.currentThread().ident != self._current_thread_ident:
            return

        if self._is_disabled():
            return

        try:
            self.disable()
            assert (
                predicate in self._known_data.existing_predicates
            ), "Cannot trace unknown predicate"
            distance_true, distance_false = ExecutionTracer._DISTANCE_COMPUTATIONS[
                cmp_op
            ](value1, value2)

            self._update_metrics(distance_false, distance_true, predicate)
        finally:
            self.enable()

    def executed_bool_predicate(self, value, predicate: int):
        """A predicate that is based on a boolean value was executed.

        Args:
            value: the value
            predicate: the predicate identifier
        """
        if threading.currentThread().ident != self._current_thread_ident:
            return

        if self._is_disabled():
            return

        try:
            self.disable()
            assert (
                predicate in self._known_data.existing_predicates
            ), "Cannot trace unknown predicate"
            distance_true = 0.0
            distance_false = 0.0
            if value:
                distance_false = 1.0
            else:
                distance_true = 1.0

            self._update_metrics(distance_false, distance_true, predicate)
        finally:
            self.enable()

    def executed_exception_match(self, err, exc, predicate: int):
        """A predicate that is based on exception matching was executed.

        Args:
            err: The raised exception
            exc: The matching condition
            predicate: the predicate identifier
        """
        if threading.currentThread().ident != self._current_thread_ident:
            return

        if self._is_disabled():
            return

        try:
            self.disable()
            assert (
                predicate in self._known_data.existing_predicates
            ), "Cannot trace unknown predicate"
            distance_true = 0.0
            distance_false = 0.0
            if given_exception_matches(err, exc):
                distance_false = 1.0
            else:
                distance_true = 1.0

            self._update_metrics(distance_false, distance_true, predicate)
        finally:
            self.enable()

    def _update_metrics(
        self, distance_false: float, distance_true: float, predicate: int
    ):
        assert (
            predicate in self._known_data.existing_predicates
        ), "Cannot update unknown predicate"
        assert distance_true >= 0.0, "True distance cannot be negative"
        assert distance_false >= 0.0, "False distance cannot be negative"
        assert (distance_true == 0.0) ^ (
            distance_false == 0.0
        ), "Exactly one distance must be 0.0, i.e., one branch must be taken."
        self._trace.executed_predicates[predicate] = (
            self._trace.executed_predicates.get(predicate, 0) + 1
        )
        self._trace.true_distances[predicate] = min(
            self._trace.true_distances.get(predicate, inf), distance_true
        )
        self._trace.false_distances[predicate] = min(
            self._trace.false_distances.get(predicate, inf), distance_false
        )

    def __repr__(self) -> str:
        return "ExecutionTracer"


def _eq(val1, val2) -> float:
    """Distance computation for '=='

    Args:
        val1: the first value
        val2: the second value

    Returns:
        the distance
    """
    if val1 == val2:
        return 0.0
    if is_numeric(val1) and is_numeric(val2):
        return abs(val1 - val2)
    if is_string(val1) and is_string(val2):
        return levenshtein_distance(val1, val2)
    if is_bytes(val1) and is_bytes(val2):
        return levenshtein_distance(
            val1.decode("iso-8859-1"), val2.decode("iso-8859-1")
        )
    return inf


def _neq(val1, val2) -> float:
    """Distance computation for '!='

    Args:
        val1: the first value
        val2: the second value

    Returns:
        the distance
    """
    if val1 != val2:
        return 0.0
    return 1.0


def _lt(val1, val2) -> float:
    """Distance computation for '<'

    Args:
        val1: the first value
        val2: the second value

    Returns:
        the distance
    """
    if val1 < val2:
        return 0.0
    if is_numeric(val1) and is_numeric(val2):
        return (val1 - val2) + 1.0
    return inf


def _le(val1, val2) -> float:
    """Distance computation for '<='

    Args:
        val1: the first value
        val2: the second value

    Returns:
        the distance
    """
    if val1 <= val2:
        return 0.0
    if is_numeric(val1) and is_numeric(val2):
        return (val1 - val2) + 1.0
    return inf


def _in(val1, val2) -> float:
    """Distance computation for 'in'

    Args:
        val1: the first value
        val2: the second value

    Returns:
        the distance
    """
    if val1 in val2:
        return 0.0
    # TODO(fk) maybe limit this to certain collections?
    # Check only if collection size is within some range,
    # otherwise the check might take very long.

    # Use smallest distance to any element.
    return min([_eq(val1, v) for v in val2] + [inf])


def _nin(val1, val2) -> float:
    """Distance computation for 'not in'

    Args:
        val1: the first value
        val2: the second value

    Returns:
        the distance
    """
    if val1 not in val2:
        return 0.0
    return 1.0


def _is(val1, val2) -> float:
    """Distance computation for 'is'

    Args:
        val1: the first value
        val2: the second value

    Returns:
        the distance
    """
    if val1 is val2:
        return 0.0
    return 1.0


def _isn(val1, val2) -> float:
    """Distance computation for 'is not'

    Args:
        val1: the first value
        val2: the second value

    Returns:
        the distance
    """
    if val1 is not val2:
        return 0.0
    return 1.0
