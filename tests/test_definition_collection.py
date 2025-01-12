import pandas as pd
import pytest

from plottable.column_def import ColumnDefinition, ColumnsInfos


@pytest.fixture
def col_defs() -> ColumnDefinition:
    return [ColumnDefinition(name=f"col{i}", title=f"Column {i}") for i in range(1, 4)]


@pytest.fixture
def col_defs_group() -> ColumnDefinition:
    coldefs = [
        ColumnDefinition(name=f"col{i}", title=f"Column {i}") for i in range(1, 4)
    ]

    coldefs[1].group = "GROUP"
    coldefs[2].group = "GROUP"

    return coldefs


@pytest.fixture
def table() -> pd.DataFrame:
    data = {"col1": ["a", "b", "c"], "col2": ["d", "e", "f"], "col3": ["g", "h", "i"]}
    df = pd.DataFrame(data)
    df.index.name = "index"

    return df


@pytest.fixture
def col_infos(col_defs, table):
    return ColumnsInfos.from_definitions_and_table(definitions=col_defs, table=table)


@pytest.fixture
def colinfos_factory():
    def col_collection(col_defs, table):
        return ColumnsInfos.from_definitions_and_table(
            definitions=col_defs, table=table
        )

    return col_collection


def test_column_infos_factory_method(col_defs, table):
    cc = ColumnsInfos.from_definitions_and_table(definitions=col_defs, table=table)

    assert isinstance(cc, ColumnsInfos)


def test_definitions_is_a_dict(col_infos):
    assert isinstance(col_infos.definitions, dict)


def test_names(col_infos):
    expected = ["index"] + [f"col{i}" for i in range(1, 4)]
    assert col_infos.names == expected


def test_titles(col_infos):
    expected = [""] + [f"Column {i}" for i in range(1, 4)]
    assert col_infos.titles == expected


def test_no_groups(col_infos):
    assert col_infos.get_columns_by_group() == {}


def test_groups(colinfos_factory, col_defs_group, table):
    col_collection = colinfos_factory(col_defs_group, table)
    expected = {"GROUP": ["col2", "col3"]}
    assert dict(col_collection.get_columns_by_group()) == expected
