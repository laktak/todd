import pytest
import datetime
from todd.tasklib import *

import pprint
pp = pprint.PrettyPrinter(indent=4).pprint

TODO_COWS = "Buy some cows +project-x @farm"
TODO_FLUX_PRIO = "(A)"
TODO_FLUX_TEXT = "Build a flux capacitor +future @weekend"
TODO_FLUX = TODO_FLUX_PRIO + " " + TODO_FLUX_TEXT
TODO_TRASH_PRIO = "(F)"
TODO_TRASH_TEXT = "Take out the trash @home due:2018-02-21"
TODO_TRASH = TODO_TRASH_PRIO + " 2000-01-01 " + TODO_TRASH_TEXT
TODO_DONE = "x 1999-01-07 Book a ticket to mars +project-x +future"
TODO_PLAN_TEXT = "Plan our summer vacation +family @weekend"
TODO_PLAN = "2001-02-03 " + TODO_PLAN_TEXT

@pytest.fixture
def tasklist():
    return Tasklist([
        TODO_COWS,
        TODO_FLUX,
        TODO_TRASH,
        TODO_DONE,
        TODO_PLAN,
    ])

@pytest.fixture
def today():
    return datetime.date.today()

def test_tasklist_init(tasklist):
    assert len(tasklist) == 5
    assert len(tasklist.get_items()) == 5

def test_tasklist_parse_entries(tasklist):
    task = tasklist.get_items()[0]
    assert task.raw == TODO_COWS
    assert task.contexts == ["@farm"]
    assert task.projects == ["+project-x"]
    assert task.priority == ""

    task = tasklist.get_items()[1]
    assert task.raw == TODO_FLUX
    assert task.contexts == ["@weekend"]
    assert task.projects == ["+future"]
    assert task.priority == "A"

    task = tasklist.get_items()[2]
    assert task.raw == TODO_TRASH
    assert task.contexts == ["@home"]
    assert task.projects == []
    assert task.due_date == "2018-02-21"
    assert task.creation_date == "2000-01-01"
    assert task.priority == "F"

    task = tasklist.get_items()[3]
    assert task.raw == TODO_DONE
    assert task.contexts == []
    assert task.projects == ["+future", "+project-x"]
    assert task.done_date == "1999-01-07"
    assert task.priority == ""

    task = tasklist.get_items()[4]
    assert task.raw == TODO_PLAN
    assert task.contexts == ["@weekend"]
    assert task.projects == ["+family"]
    assert task.priority == ""

def test_tasklist_iterable(tasklist):
    for task in tasklist:
        assert task.raw != ""
    for task in tasklist:
        assert task.raw != ""

def test_context_project_regex(tasklist):
    tasklist.set_text_items([
        TODO_COWS + " foo@email.com @email",
        TODO_FLUX + " NotA+Project +project-y",
        TODO_TRASH,
        TODO_DONE,
        TODO_PLAN])
    task = tasklist[0]
    assert task.contexts == ["@email", "@farm"]
    assert task.projects == ["+project-x"]
    task = tasklist[1]
    assert task.contexts == ["@weekend"]
    assert task.projects == ["+future", "+project-y"]

def test_tasklist_all_contexts(tasklist):
    assert ["@farm", "@home", "@weekend"] == tasklist.all_contexts()

def test_tasklist_all_projects(tasklist):
    assert ["+family", "+future", "+project-x"] == tasklist.all_projects()

def test_tasklist_done_date(tasklist):
    assert Task.scan_done_date(TODO_COWS) == ""
    assert Task.scan_done_date(TODO_FLUX) == ""
    assert Task.scan_done_date(TODO_DONE) == "1999-01-07"

def test_tasklist_creation_date(tasklist):
    assert Task.scan_creation_date("2011-03-02 " + TODO_COWS) == "2011-03-02"

def test_tasklist_due_date(tasklist):
    assert Task.scan_due_date(TODO_TRASH) == "2018-02-21"

def test_tasklist_priority(tasklist):
    assert Task.scan_priority("(A) Priority A") == "A"
    assert Task.scan_priority("(Z) Priority Z") == "Z"
    assert Task.scan_priority("(a) No Priority") == ""
    # with pytest.raises(task.NoPriorityError):
    assert Task.scan_priority("No Priority (A)") == ""
    assert Task.scan_priority("(A)No Priority") == ""
    assert Task.scan_priority("(A)->No Priority") == ""

def test_tasklist_sorted(tasklist):
    tasklist.set_text_items([
        TODO_FLUX,
        TODO_COWS,
        TODO_TRASH,
        TODO_DONE,
        TODO_PLAN,
    ])
    assert [task.task_id for task in tasklist.get_items()] == [6, 7, 8, 9, 10]

    assert [task.task_id for task in tasklist.get_items_sorted("due")] == [
        8, 6, 10, 7, 9]

    assert [task.task_id for task in tasklist.get_items_sorted("prio")] == [
        6, 8, 10, 7, 9]

def test_tasklist_filter_context(tasklist):
    assert [t.task_id for t in Tasklist.filter_context(tasklist.get_items(), "@weekend")] == [
        2, 5]

def test_tasklist_set_items(tasklist):
    tasklist.set_text_items([
        TODO_FLUX,
        TODO_TRASH,
        TODO_DONE,
        "2000-01-02 " + TODO_PLAN])
    assert [t.raw for t in tasklist] == [
        TODO_FLUX,
        TODO_TRASH,
        TODO_DONE,
        "2000-01-02 " + TODO_PLAN]
    assert tasklist[3].creation_date == "2000-01-02"

def test_tasklist_set_done(tasklist, today):
    tasklist[0].set_done()
    tasklist[1].set_done()
    assert [t.raw for t in tasklist] == [
        "x {} {}".format(today, TODO_COWS),
        "x {} {}".format(today, TODO_FLUX_TEXT),
        TODO_TRASH,
        TODO_DONE,
        TODO_PLAN]
    assert [t.is_done() for t in tasklist] == [True, True, False, True, False]
    tasklist[1].set_done(False)
    assert tasklist[1].raw == TODO_FLUX_TEXT
    assert tasklist[1].done_date == ""

def test_task_undo(tasklist):
    tasklist.set_text_items([
        TODO_TRASH,
        TODO_DONE,
        TODO_PLAN])
    assert tasklist[1].creation_date == ""
    assert tasklist[1].done_date == "1999-01-07"
    tasklist[1].set_done(False)
    assert tasklist[1].creation_date == ""
    assert tasklist[1].done_date == ""

def test_task_is_done(tasklist):
    tasklist.set_text_items([
        TODO_COWS,
        TODO_TRASH,
        TODO_DONE,
    ])
    assert [t.is_done() for t in tasklist] == [
        False,
        False,
        True]

def test_task_set_creation_date(tasklist, today):
    tasklist[0].set_creation_date(today)
    assert tasklist[0].raw == "{} {}".format(today, TODO_COWS)
    assert tasklist[0].creation_date == today.isoformat()
    tasklist[1].set_creation_date(today)
    assert tasklist[1].raw == "{} {} {}".format(TODO_FLUX_PRIO, today, TODO_FLUX_TEXT)
    assert tasklist[1].creation_date == today.isoformat()
    tasklist[2].set_creation_date(today)
    assert tasklist[2].raw == "{} {} {}".format(TODO_TRASH_PRIO, today, TODO_TRASH_TEXT)
    assert tasklist[2].creation_date == today.isoformat()
    tasklist[4].set_creation_date(today)
    assert tasklist[4].raw == "{} {}".format(today, TODO_PLAN_TEXT)
    assert tasklist[4].creation_date == today.isoformat()

def test_tasklist_append(tasklist, today):
    tasklist.insert_new(-1, "THIS IS A TEST @testing")
    assert [t.raw for t in tasklist] == [
        TODO_COWS,
        TODO_FLUX,
        TODO_TRASH,
        TODO_DONE,
        TODO_PLAN,
        "THIS IS A TEST @testing",
    ]
    assert [task.task_id for task in tasklist.get_items()] == [1, 2, 3, 4, 5, 6]

def test_tasklist_delete(tasklist):
    tasklist.delete_by_id(1)
    assert [t.raw for t in tasklist] == [
        TODO_FLUX,
        TODO_TRASH,
        TODO_DONE,
        TODO_PLAN]
    assert [task.task_id for task in tasklist.get_items()] == [2, 3, 4, 5]
    tasklist.delete_by_id(5)
    assert [t.raw for t in tasklist] == [
        TODO_FLUX,
        TODO_TRASH,
        TODO_DONE]
    assert [task.task_id for task in tasklist.get_items()] == [2, 3, 4]

def test_tasklist_insert(tasklist, today):
    tasklist.insert_new(1, "THIS IS A TEST @testing")
    assert [t.raw for t in tasklist] == [
        TODO_COWS,
        "THIS IS A TEST @testing",
        TODO_FLUX,
        TODO_TRASH,
        TODO_DONE,
        TODO_PLAN,
    ]
    assert [task.task_id for task in tasklist.get_items()] == [1, 6, 2, 3, 4, 5]

def test_tasklist_search(tasklist):
    search = Tasklist.prep_search("future")
    assert [t.raw for t in Tasklist.search(search, tasklist.get_items())] == [
        TODO_FLUX,
        TODO_DONE]

def test_set_priority(tasklist):
    tasklist[0].set_priority("F")
    assert tasklist[0].raw == "(F) " + TODO_COWS
    tasklist[0].set_priority("")
    assert tasklist[0].raw == TODO_COWS
    tasklist[1].set_priority("")
    assert tasklist[1].raw == TODO_FLUX_TEXT
