import pytest


@pytest.fixture
def func_args_1():
    return {"node": 1, "status": {1: "S", 2: "S", 3: "I"}, "edge": [1, 2, 3]}


@pytest.fixture
def func_args_2():
    return {"node": 1, "status": {1: "S", 2: "I", 3: "I"}, "edge": [1, 2, 3]}


@pytest.fixture
def func_args_3():
    return {"node": 2, "status": {1: "S", 2: "I", 3: "I", 4: "R"}, "edge": [1, 2, 3, 4]}


@pytest.fixture
def func_args_4():
    return {
        "node": 5,
        "status": {1: "S", 2: "I", 3: "I", 4: "R", 5: "S"},
        "edge": [1, 2, 3, 4, 5],
    }


@pytest.fixture
def func_args_5():
    return {
        "node": 3,
        "status": {1: "I", 2: "I", 3: "S", 4: "I", 5: "I"},
        "edge": [1, 2, 3, 4, 5],
    }


@pytest.fixture
def func_args_6():
    return {
        "node": 3,
        "status": {1: "S", 2: "S", 3: "S", 4: "R", 5: "R"},
        "edge": [1, 2, 3, 4, 5],
    }
