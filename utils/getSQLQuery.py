def executeSQLQuery(
    query: str,
    session,
    columnPosition: None | int = None,
    havingClause: None | str = None,
):
    result = session.execute(query)
    # TODO: modify this function so that it does only the execution part
    metadata = {"columnPosition": columnPosition, "havingClause": havingClause}
    columnNames = list(result.keys())
    results = result.all()
    data = [dict(zip(columnNames, row)) for row in results]
    return {"metadata": metadata, "data": data}


def getWherePredicate(**kwargs):
    filteredKwargs = []
    for key, value in kwargs.items():
        if value is not None:
            filteredKwargs.append((key, value))
    wherePredicate = " AND ".join(f"{key}={value!r}" for key, value in filteredKwargs)
    return wherePredicate
