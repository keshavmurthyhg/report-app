from modules.search.filters import apply_filters
from modules.search.search import apply_search


def apply_all_filters(df, status, priority, keyword):

    # Status filter
    if status:
        df = df[df["Status"].isin(status)]

    # Priority filter
    if priority:
        df = df[df["Priority"].isin(priority)]

    # Keyword search
    df = apply_search(df, keyword)

    return df
