#  This file is part of Pynguin.
#
#  SPDX-FileCopyrightText: 2019–2020 Pynguin Contributors
#
#  SPDX-License-Identifier: LGPL-3.0-or-later
#
import ast

import pytest

from pynguin.analyses.seeding.initialpopulationseeding import _TestTransformer
from pynguin.generation.export.exportprovider import ExportProvider
from pynguin.setup.testclustergenerator import TestClusterGenerator


@pytest.mark.parametrize(
    "testcase_seed",
    [
        (
            """    var0 = 1.1
    var1 = module0.positional_only(var0)
"""
        ),
        (
            """    var0 = 1.1
    var1 = 42
    var2 = []
    var3 = 'test'
    var4 = 'key'
    var5 = 'value'
    var6 = {var4: var5}
    var7 = module0.all_params(var0, var1, *var2, param4=var3, **var6)
"""
        ),
    ],
)
def test_parameter_mapping_roundtrip(testcase_seed, tmp_path):
    testcase_seed = (
        """# Automatically generated by Pynguin.
import tests.fixtures.grammar.parameters as module0


def test_case_0():
"""
        + testcase_seed
    )
    test_cluster = TestClusterGenerator(
        "tests.fixtures.grammar.parameters"
    ).generate_cluster()
    transformer = _TestTransformer(test_cluster)
    transformer.visit(ast.parse(testcase_seed))
    export_path = tmp_path / "export.py"
    ExportProvider.get_exporter().export_sequences(export_path, transformer.testcases)
    with open(export_path) as f:
        content = f.read()
        assert content == testcase_seed
