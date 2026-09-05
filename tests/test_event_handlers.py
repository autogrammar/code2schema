import copy
import re

from code2schema.analyzer.events import DomainEvent, _find_handlers
from code2schema.core.models import FunctionIR, ModuleIR


def test_handler_matching_preserves_order_duplicates_case_and_empty_keywords():
    names = ["UserEvent", "UserEvent", "Event", "Entity1Event", "Entity10Event", "ŻółćEvent"]
    events = [DomainEvent(name=n, emitted_by=str(i), handled_by=["existing"]) for i,n in enumerate(names)]
    modules = [ModuleIR(name=m, path=m+".py", functions=[FunctionIR(name=n,module=m) for n in [
        "handle_user", "ON_USER", "handle_entity10", "on_żółć", "plain_user", "consumer_user"]]) for m in ["a","b"]]
    expected = copy.deepcopy(events)
    for _ in range(2):
        for mod in modules:
            for f in mod.functions:
                if re.search(r"(on_|handle_|listener|subscriber|consumer|process_|receive_)", f.name, re.I):
                    for ev in expected:
                        keyword = ev.name.lower().replace("event", "").strip()
                        if keyword and keyword in f.name.lower():
                            ev.handled_by.append(f.qualified_name)
        _find_handlers(events, modules)
    assert events == expected


def test_empty_events_and_modules_are_noops():
    events = [DomainEvent(name="UserEvent", emitted_by="emit")]
    _find_handlers(events, [])
    _find_handlers([], [])
    assert events[0].handled_by == []
