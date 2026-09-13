def run_one(record, schema, root_lock, checker, guard):
    first = checker(record, schema, root_lock)
    second = checker(record, schema, root_lock)
    final = guard(record, first)
    return {
        "first": first,
        "second": second,
        "final": final,
    }
