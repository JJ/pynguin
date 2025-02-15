#  This file is part of Pynguin.
#
#  SPDX-FileCopyrightText: 2019–2020 Pynguin Contributors
#
#  SPDX-License-Identifier: LGPL-3.0-or-later
#
from unittest import mock
from unittest.mock import MagicMock

from pynguin.generation.algorithms.mioarchive import (
    MIOArchive,
    Population,
    PopulationPair,
)


def test_population_pair():
    pair = PopulationPair(0.5, MagicMock())
    assert pair == pair


def test_population_initial_counter():
    population = Population(1)
    assert population.counter == 0


def test_population_not_covered():
    population = Population(1)
    assert not population.is_covered


def test_population_is_covered():
    population = Population(1)
    best_solution = MagicMock()
    population.add_solution(1.0, best_solution)
    assert population.is_covered


def test_population_add_solution_covered():
    population = Population(5)
    best_solution = MagicMock()
    population.add_solution(1.0, best_solution)
    assert population.num_solutions == 1


def test_population_add_solution_worst():
    population = Population(5)
    best_solution = MagicMock()
    population.add_solution(0.0, best_solution)
    assert population.num_solutions == 0


def test_population_add_solution_already_covered():
    population = Population(5)
    best_solution = MagicMock()
    good_solution = MagicMock()
    population.add_solution(1.0, best_solution)
    assert population.add_solution(0.5, good_solution) is False


def test_population_add_solution_replace_best():
    population = Population(5)
    good_solution = MagicMock()
    better_solution = MagicMock()
    population.add_solution(1.0, good_solution)
    with mock.patch.object(population, "_is_pair_better_than_current") as better_mock:
        better_mock.return_value = True
        assert population.add_solution(1.0, better_solution) is True
        better_mock.assert_called_with(
            PopulationPair(1.0, good_solution), PopulationPair(1.0, better_solution)
        )
        assert population.get_best_solution_if_any() == better_solution


def test_population_add_solution_shrink():
    population = Population(2)
    good_solution = MagicMock()
    population.add_solution(0.5, MagicMock())
    population.add_solution(0.5, MagicMock())
    assert population.num_solutions == 2
    assert population.add_solution(1.0, good_solution) is True
    assert population.get_best_solution_if_any() == good_solution
    assert population.num_solutions == 1


def test_population_add_solution_still_space():
    population = Population(5)
    population.add_solution(0.5, MagicMock())
    population.add_solution(0.5, MagicMock())
    population.add_solution(0.5, MagicMock())
    population.add_solution(0.5, MagicMock())
    assert population.add_solution(0.5, MagicMock()) is True
    assert population.num_solutions == 5


def test_population_add_solution_replace_worst():
    population = Population(5)
    population.add_solution(0.1, MagicMock())
    population.add_solution(0.2, MagicMock())
    population.add_solution(0.3, MagicMock())
    population.add_solution(0.4, MagicMock())
    population.add_solution(0.5, MagicMock())
    with mock.patch.object(population, "_is_pair_better_than_current") as better_mock:
        better_mock.return_value = True
        assert population.add_solution(0.6, MagicMock()) is True
        assert population.num_solutions == 5


def test_population_add_solution_to_bad():
    population = Population(5)
    population.add_solution(0.1, MagicMock())
    population.add_solution(0.2, MagicMock())
    population.add_solution(0.3, MagicMock())
    population.add_solution(0.4, MagicMock())
    population.add_solution(0.5, MagicMock())
    with mock.patch.object(population, "_is_pair_better_than_current") as better_mock:
        better_mock.return_value = False
        assert population.add_solution(0.01, MagicMock()) is False
        assert population.num_solutions == 5


def test_population_sample_solution():
    population = Population(5)
    solution = MagicMock()
    population.add_solution(0.1, solution)
    assert population.sample_solution() == solution
    assert population.counter == 1


def test_population_sample_solution_reset():
    population = Population(5)
    solution = MagicMock()
    population.add_solution(0.1, solution)
    assert population.sample_solution() == solution
    assert population.counter == 1
    assert population.add_solution(0.01, solution) is True
    assert population.counter == 0


def test_population_no_solution():
    population = Population(5)
    assert population.get_best_solution_if_any() is None


def test_population_shrink_solution():
    population = Population(3)
    population.add_solution(0.5, MagicMock())
    population.add_solution(0.5, MagicMock())
    population.add_solution(0.5, MagicMock())
    population.shrink_population(1)
    assert population.num_solutions == 1


def test_population_shrink_solution_already_covered():
    population = Population(3)
    with mock.patch.object(population, "_is_pair_better_than_current") as better_mock:
        better_mock.return_value = False
        population.add_solution(1.0, MagicMock())
        population.add_solution(1.0, MagicMock())
        population.add_solution(1.0, MagicMock())
        population.shrink_population(1)
        assert population.num_solutions == 1


def test_population_make_sure_sorted():
    population = Population(3)
    with mock.patch.object(population, "_is_pair_better_than_current") as better_mock:
        better_mock.return_value = False
        first = MagicMock()
        second = MagicMock()
        third = MagicMock()
        population.add_solution(0.2, second)
        population.add_solution(0.1, first)
        population.add_solution(0.3, third)
        assert [p.test_case_chromosome for p in population._solutions] == [
            third,
            second,
            first,
        ]


def test_is_better():
    better = PopulationPair(1.0, MagicMock())
    worse = PopulationPair(0.9, MagicMock())
    assert Population._is_pair_better_than_current(worse, better) is True


def test_is_worse():
    better = PopulationPair(1.0, MagicMock())
    worse = PopulationPair(0.9, MagicMock())
    assert Population._is_pair_better_than_current(better, worse) is False


def test_is_even_secondary():
    better = PopulationPair(1.0, MagicMock())
    worse = PopulationPair(1.0, MagicMock())
    with mock.patch.object(Population, "_is_better_than_current") as better_mock:
        better_mock.return_value = 42
        assert Population._is_pair_better_than_current(better, worse) == 42


def test_is_better_secondary_timeout():
    result_timeout = MagicMock(timeout=True)
    result_ok = MagicMock(timeout=False)
    result_ok.has_test_exceptions.return_value = False

    better = MagicMock()
    better.get_last_execution_result.return_value = result_ok
    worse = MagicMock()
    worse.get_last_execution_result.return_value = result_timeout
    assert Population._is_better_than_current(worse, better) is True


def test_is_better_secondary_exception():
    result_timeout = MagicMock(timeout=False)
    result_timeout.has_test_exceptions.return_value = True
    result_ok = MagicMock(timeout=False)
    result_ok.has_test_exceptions.return_value = False

    better = MagicMock()
    better.get_last_execution_result.return_value = result_ok
    worse = MagicMock()
    worse.get_last_execution_result.return_value = result_timeout
    assert Population._is_better_than_current(worse, better) is True


def test_is_better_secondary_not_better():
    result_timeout = MagicMock(timeout=True)
    result_timeout.has_test_exceptions.return_value = True
    result_ok = MagicMock(timeout=True)
    result_ok.has_test_exceptions.return_value = True

    better = MagicMock()
    better.size.return_value = 3
    better.get_last_execution_result.return_value = result_ok
    worse = MagicMock()
    worse.get_last_execution_result.return_value = result_timeout
    worse.size.return_value = 5
    assert Population._is_better_than_current(worse, better) is True


def test_is_better_secondary_no_timeout_or_exception():
    result_ok = MagicMock(timeout=False)
    result_ok.has_test_exceptions.return_value = False

    better = MagicMock()
    better.size.return_value = 3
    better.get_last_execution_result.return_value = result_ok
    worse = MagicMock()
    worse.get_last_execution_result.return_value = result_ok
    worse.size.return_value = 5
    assert Population._is_better_than_current(worse, better) is True


def test_is_better_secondary_no_timeout_or_exception_swapped():
    result_ok = MagicMock(timeout=False)
    result_ok.has_test_exceptions.return_value = False

    better = MagicMock()
    better.size.return_value = 3
    better.get_last_execution_result.return_value = result_ok
    worse = MagicMock()
    worse.get_last_execution_result.return_value = result_ok
    worse.size.return_value = 5
    assert Population._is_better_than_current(better, worse) is False


def test_archive_initial_empty():
    fitness = MagicMock()
    archive = MIOArchive([fitness], 3)
    assert archive.num_covered_targets == 0
    assert archive.get_solutions() == []


def test_archive_update_no_ex():
    fitness = MagicMock()
    archive = MIOArchive([fitness], 3)
    solution = MagicMock()
    clone = MagicMock()
    solution.clone.return_value = clone
    clone.get_fitness_for.return_value = 1.0
    result = MagicMock()
    result.has_test_exceptions.return_value = False
    clone.get_last_execution_result.return_value = result
    assert archive.update_archive(solution) is True


def test_archive_update_ex():
    fitness = MagicMock()
    archive = MIOArchive([fitness], 3)
    solution = MagicMock()
    clone = MagicMock()
    solution.clone.return_value = clone
    clone.get_fitness_for.return_value = 1.0
    result = MagicMock()
    result.has_test_exceptions.return_value = True
    clone.get_last_execution_result.return_value = result
    clone.get_last_mutatable_statement.return_value = 3
    test_case = MagicMock()
    clone.test_case = test_case
    assert archive.update_archive(solution) is True
    test_case.chop.assert_called_with(3)


def test_archive_get_solution_none_covered():
    fitness = MagicMock()
    archive = MIOArchive([fitness], 3)
    assert archive.get_solution() is None


def test_archive_get_solution_is_covered():
    fitness = MagicMock()
    archive = MIOArchive([fitness], 3)
    solution = MagicMock()
    clone = MagicMock()
    solution.clone.return_value = clone
    clone.get_fitness_for.return_value = 0.0
    second_clone = MagicMock()
    clone.clone.return_value = second_clone
    archive.update_archive(solution)
    assert archive.get_solution() == second_clone


def test_archive_get_solution_not_covered():
    fitness = MagicMock()
    archive = MIOArchive([fitness], 3)
    solution = MagicMock()
    clone = MagicMock()
    solution.clone.return_value = clone
    clone.get_fitness_for.return_value = 0.5
    second_clone = MagicMock()
    clone.clone.return_value = second_clone
    archive.update_archive(solution)
    assert archive.get_solution() == second_clone


def test_archive_get_solutions():
    fitness = MagicMock()
    archive = MIOArchive([fitness], 3)
    solution = MagicMock()
    clone = MagicMock()
    solution.clone.return_value = clone
    clone.get_fitness_for.return_value = 0.0
    archive.update_archive(solution)
    assert archive.get_solutions() == [clone]


def test_archive_num_covered_targets():
    fitness = MagicMock()
    archive = MIOArchive([fitness], 3)
    solution = MagicMock()
    clone = MagicMock()
    solution.clone.return_value = clone
    clone.get_fitness_for.return_value = 0.0
    archive.update_archive(solution)
    assert archive.num_covered_targets == 1
