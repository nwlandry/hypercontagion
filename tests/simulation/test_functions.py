from hypercontagion import collective_contagion, individual_contagion, threshold, majority_vote, size_dependent


def test_collective_contagion(func_args_1, func_args_2, func_args_3, func_args_4, func_args_5):
    assert collective_contagion(func_args_1["node"], func_args_1["status"], func_args_1["edge"]) == 0
    assert collective_contagion(func_args_2["node"], func_args_2["status"], func_args_2["edge"]) == 1
    assert collective_contagion(func_args_3["node"], func_args_3["status"], func_args_3["edge"]) == 0
    assert collective_contagion(func_args_4["node"], func_args_4["status"], func_args_4["edge"]) == 0
    assert collective_contagion(func_args_5["node"], func_args_5["status"], func_args_5["edge"]) == 1


def test_individual_contagion(func_args_1, func_args_2, func_args_3, func_args_4, func_args_5, func_args_6):
    assert individual_contagion(func_args_1["node"], func_args_1["status"], func_args_1["edge"]) == 1
    assert individual_contagion(func_args_2["node"], func_args_2["status"], func_args_2["edge"]) == 1
    assert individual_contagion(func_args_3["node"], func_args_3["status"], func_args_3["edge"]) == 1
    assert individual_contagion(func_args_4["node"], func_args_4["status"], func_args_4["edge"]) == 1
    assert individual_contagion(func_args_6["node"], func_args_6["status"], func_args_6["edge"]) == 0


def test_threshold(func_args_1, func_args_2, func_args_3, func_args_4):
    assert threshold(func_args_1["node"], func_args_1["status"], func_args_1["edge"]) == 1
    assert threshold(func_args_1["node"], func_args_1["status"], func_args_1["edge"], threshold=0.51) == 0
    assert threshold(func_args_2["node"], func_args_2["status"], func_args_2["edge"]) == 1
    assert threshold(func_args_3["node"], func_args_3["status"], func_args_3["edge"]) == 0
    assert threshold(func_args_3["node"], func_args_3["status"], func_args_3["edge"], threshold=0.3) == 1
    assert threshold(func_args_4["node"], func_args_4["status"], func_args_4["edge"]) == 1
    assert threshold(func_args_4["node"], func_args_4["status"], func_args_4["edge"], threshold=0.51) == 0


def test_majority_vote(func_args_1, func_args_2, func_args_3, func_args_4, func_args_5):
    assert majority_vote(func_args_1["node"], func_args_1["status"], func_args_1["edge"]) in {0, 1}
    assert majority_vote(func_args_2["node"], func_args_2["status"], func_args_2["edge"]) == 1
    assert majority_vote(func_args_3["node"], func_args_3["status"], func_args_3["edge"]) == 0
    assert majority_vote(func_args_4["node"], func_args_4["status"], func_args_4["edge"]) in {0, 1}
    assert majority_vote(func_args_5["node"], func_args_5["status"], func_args_5["edge"]) == 1

def test_size_dependent(func_args_1, func_args_2, func_args_3, func_args_4, func_args_5):
    assert size_dependent(func_args_1["node"], func_args_1["status"], func_args_1["edge"]) == 1
    assert size_dependent(func_args_2["node"], func_args_2["status"], func_args_2["edge"]) == 2
    assert size_dependent(func_args_3["node"], func_args_3["status"], func_args_3["edge"]) == 1
    assert size_dependent(func_args_4["node"], func_args_4["status"], func_args_4["edge"]) == 2
    assert size_dependent(func_args_5["node"], func_args_5["status"], func_args_5["edge"]) == 4