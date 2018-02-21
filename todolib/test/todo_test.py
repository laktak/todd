import pytest
from datetime import date
from todolib import *

import pprint
pp = pprint.PrettyPrinter(indent=4).pprint

TODO_COWS="Buy some cows +project-x @farm"
TODO_FLUX="(A) Build a flux capacitor +future @weekend"
TODO_TRASH="(F) Take out the trash @home due:2018-02-21"
TODO_DONE="x 1999-01-07 Book a ticket to mars +project-x +future"
TODO_PLAN="Plan our summer vacation +family @weekend"

@pytest.fixture
def todos():
    return Todos([
        TODO_COWS,
        TODO_FLUX,
        TODO_TRASH,
        TODO_DONE,
        TODO_PLAN,
    ])

@pytest.fixture
def today():
    return date.today()

def test_todos_init(todos):
    assert len(todos) == 5
    assert len(todos.get_items()) == 5

def test_todos_parse_entries(todos):
    todo = todos.get_items()[0]
    assert todo.raw == TODO_COWS
    assert todo.contexts == ["@farm"]
    assert todo.projects == ["+project-x"]
    assert todo.priority == ""

    todo = todos.get_items()[1]
    assert todo.raw == TODO_FLUX
    assert todo.contexts == ["@weekend"]
    assert todo.projects == ["+future"]
    assert todo.priority == "A"

    todo = todos.get_items()[2]
    assert todo.raw == TODO_TRASH
    assert todo.contexts == ["@home"]
    assert todo.projects == []
    assert todo.due_date == "2018-02-21"
    assert todo.priority == "F"

    todo = todos.get_items()[3]
    assert todo.raw == TODO_DONE
    assert todo.contexts == []
    assert todo.projects == ["+future", "+project-x"]
    assert todo.done_date == "1999-01-07"
    assert todo.priority == ""

    todo = todos.get_items()[4]
    assert todo.raw == TODO_PLAN
    assert todo.contexts == ["@weekend"]
    assert todo.projects == ["+family"]
    assert todo.priority == ""

def test_todos_iterable(todos):
    for todo in todos:
        assert todo.raw != ""
    for todo in todos:
        assert todo.raw != ""

def test_context_project_regex(todos):
    todos.set_items([
        TODO_COWS + " foo@email.com @email",
        TODO_FLUX + " NotA+Project +project-y",
        TODO_TRASH,
        TODO_DONE,
        TODO_PLAN])
    todo = todos[0]
    assert todo.contexts == ["@email", "@farm"]
    assert todo.projects == ["+project-x"]
    todo = todos[1]
    assert todo.contexts == ["@weekend"]
    assert todo.projects == ["+future", "+project-y"]

def test_todos_all_contexts(todos):
    assert ["@farm", "@home", "@weekend"] == todos.all_contexts()

def test_todos_all_projects(todos):
    assert ["+family", "+future", "+project-x"] == todos.all_projects()

def test_todos_done_date(todos):
    assert Todo.scan_done_date(TODO_COWS) == ""
    assert Todo.scan_done_date(TODO_FLUX) == ""
    assert Todo.scan_done_date(TODO_DONE) == "1999-01-07"

def test_todos_creation_date(todos):
    assert Todo.scan_creation_date("2011-03-02 " + TODO_COWS) == "2011-03-02"

def test_todos_due_date(todos):
    assert Todo.scan_due_date(TODO_TRASH) == "2018-02-21"

def test_todos_priority(todos):
    assert Todo.scan_priority("(A) Priority A") == "A"
    assert Todo.scan_priority("(Z) Priority Z") == "Z"
    assert Todo.scan_priority("(a) No Priority") == ""
    # with pytest.raises(todo.NoPriorityError):
    assert Todo.scan_priority("No Priority (A)") == ""
    assert Todo.scan_priority("(A)No Priority") == ""
    assert Todo.scan_priority("(A)->No Priority") == ""

def test_todos_sorted(todos):
    todos.set_items([
        TODO_FLUX,
        TODO_COWS,
        TODO_TRASH,
        TODO_DONE,
        TODO_PLAN,
    ])
    assert [todo.raw_index for todo in todos.get_items()] == [0, 1, 2, 3, 4]

    assert [todo.raw_index for todo in todos.get_items_sorted("due")] == [
        2, 0, 1, 4, 3]

    assert [todo.raw_index for todo in todos.get_items_sorted("prio")] == [
        0, 2, 1, 4, 3]

def test_todos_filter_context(todos):
    assert [t.raw_index for t in Todos.filter_context(todos.get_items(), "@weekend")] == [
        1, 4]

def test_todos_set_items(todos):
    todos.set_items([
        TODO_FLUX,
        TODO_TRASH,
        TODO_DONE,
        TODO_PLAN])
    assert [t.raw for t in todos] == [
        TODO_FLUX,
        TODO_TRASH,
        TODO_DONE,
        TODO_PLAN]

def test_todos_set_done(todos, today):
    todos[0].set_done()
    todos[1].set_done()
    assert [t.raw for t in todos] == [
        "x {} {}".format(today, TODO_COWS),
        "x {} {}".format(today, TODO_FLUX),
        TODO_TRASH,
        TODO_DONE,
        TODO_PLAN]
    assert [t.is_done() for t in todos] == [True, True, False, True, False]
    todos[1].set_done(False)
    assert todos[1].raw == TODO_FLUX
    assert todos[1].done_date == ""

def test_todo_undo(todos):
    todos.set_items([
        TODO_TRASH,
        TODO_DONE,
        TODO_PLAN])
    assert todos[1].creation_date == ""
    assert todos[1].done_date == "1999-01-07"
    todos[1].set_done(False)
    assert todos[1].creation_date == ""
    assert todos[1].done_date == ""

def test_todo_is_done(todos):
    todos.set_items([
        TODO_COWS,
        TODO_TRASH,
        TODO_DONE,
    ])
    assert [t.is_done() for t in todos] == [
        False,
        False,
        True]

def test_todo_add_creation_date(todos, today):
    todos[2].add_creation_date()
    assert todos[2].raw == "{} {} {}".format(TODO_TRASH[:3], today, TODO_TRASH[4:])
    assert todos[2].creation_date == "{}".format(today)

def test_todos_append(todos, today):
    todos.append("THIS IS A TEST @testing")
    assert [t.raw for t in todos] == [
        TODO_COWS,
        TODO_FLUX,
        TODO_TRASH,
        TODO_DONE,
        TODO_PLAN,
        "THIS IS A TEST @testing",
    ]
    assert [todo.raw_index for todo in todos.get_items()] == [0, 1, 2, 3, 4, 5]

def test_todos_delete(todos):
    todos.delete(0)
    assert [t.raw for t in todos] == [
        TODO_FLUX,
        TODO_TRASH,
        TODO_DONE,
        TODO_PLAN]
    assert [todo.raw_index for todo in todos.get_items()] == [0, 1, 2, 3]
    todos.delete(3)
    assert [t.raw for t in todos] == [
        TODO_FLUX,
        TODO_TRASH,
        TODO_DONE]
    assert [todo.raw_index for todo in todos.get_items()] == [0, 1, 2]

def test_todos_insert(todos, today):
    todos.insert(1, "THIS IS A TEST @testing")
    assert [t.raw for t in todos] == [
        TODO_COWS,
        "THIS IS A TEST @testing",
        TODO_FLUX,
        TODO_TRASH,
        TODO_DONE,
        TODO_PLAN,
    ]
    assert [todo.raw_index for todo in todos.get_items()] == [0, 1, 2, 3, 4, 5]

def test_todos_search(todos):
    search = Todos.prep_search("future")
    assert [t.raw for t in Todos.search(search, todos.get_items())] == [
        TODO_FLUX,
        TODO_DONE]

def test_change_priority(todos):
    todos[0].change_priority("F")
    assert todos[0].raw == "(F) " + TODO_COWS
    todos[0].change_priority("")
    assert todos[0].raw == TODO_COWS
