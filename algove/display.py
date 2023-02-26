from functools import singledispatch
from typing import Callable


def truncated_print(n_chars: int) -> Callable:
    def trunc_print(name: str, obj):
        header = f"###### {name} ######\n"
        print(header)
        print("\n".join(str(obj).splitlines()[:n_chars]))
        print(f"\n#### end {name} ####\n")

    return trunc_print

import streamlit as st

@singledispatch
def streamlit_repr(obj, short: bool = True):
    return st.text(str(obj))

@streamlit_repr.register
def streamlit_text(obj: str, short: bool = True):
    return st.text("\n".join(obj.splitlines()[:10]))

from algove.pipeline import Pipeline

@streamlit_repr.register
def streamlit_pipeine(obj: Pipeline, short: bool = True):
    for step in obj.funcs:
        st.text(str(step.__qualname__))

import polars as pl
@streamlit_repr.register
def streamlit_polars(obj: pl.DataFrame, short: bool =True):
    if short:
        return st.dataframe(obj.limit(10).to_pandas())
    return st.dataframe(obj.to_pandas())


def streamlit_display(short: bool = True) -> Callable:
    def st_display(name: str, obj):
        st.markdown(f"## {name}")
        streamlit_repr(obj)

    return st_display