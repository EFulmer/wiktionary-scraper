import re

import pandas as pd
import requests
from bs4 import BeautifulSoup
from lxml import etree


API_ROOT = "https://en.wiktionary.org/api/rest_v1/page/title/"


def get_inflection_tables(word: str) -> list[pd.DataFrame]:
    """Get the inflection tables for all entries Wiktionary has for
    `word`.
    """
    response = requests.get(f"{API_ROOT}{word}")
    response.raise_for_status()
    soup = BeautifulSoup(r.content, "lxml")
    inflection_tables = soup.find_all("table", class_=lambda c: c and "inflection" in c)
    dfs = [pd.read_html(str(table))[0] for table in inflection_tables]
    return dfs


def extract_case(inflections_df: pd.DataFrame, case: str) -> pd.DataFrame:
    """Given a table of inflections for a noun or adjective, over all
    cases and persons, extract the inflections for each person in that
    case. e.g. if given an inflection table for Ukrainian and a case
    value of "nominative," returns a one-row `DataFrame` with all
    nominative case forms of the noun/adjective.
    """
    # Cleanup, maybe best to move to a separate function called earlier
    # at some point in the future.
    # Remove rows that are all NaN
    inflections_df = inflections_df.dropna(how="all")

    # Filter for the target case in the first column
    boolean_indexer = inflections_df.iloc[:, 0] \
        .astype(str).str.lower().str.contains(case.lower())
    declensions = inflections_df[boolean_indexer]

    # Remove any parenthesized content
    # (e.g., pronunciations like "(jevó)")
    declensions = declensions.map(
        lambda x: re.sub(r"\s*\([^)]*\)", "", str(x)) if pd.notna(x) else x
    )

    return declensions
