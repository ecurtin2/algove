from functools import singledispatch
from typing import Callable
from algove.pipeline import Pipeline


import polars as pl
import streamlit as st


def truncated_print(n_chars: int) -> Callable:
    def trunc_print(name: str, obj):
        header = f"###### {name} ######\n"
        print(header)
        print("\n".join(str(obj).splitlines()[:n_chars]))
        print(f"\n#### end {name} ####\n")

    return trunc_print


@singledispatch
def streamlit_repr(obj, short: bool = True):
    return st.text(str(obj))


@streamlit_repr.register
def streamlit_text(obj: str, short: bool = True):
    return st.text("\n".join(obj.splitlines()[:10]))


@streamlit_repr.register
def streamlit_pipeine(obj: Pipeline, short: bool = True):
    for step in obj.funcs:
        st.text(str(step.__qualname__))


@streamlit_repr.register
def streamlit_polars(obj: pl.DataFrame, short: bool = True):
    if short:
        return st.dataframe(obj.limit(10).to_pandas())
    return st.dataframe(obj.to_pandas())


def streamlit_display(short: bool = True) -> Callable:
    def st_display(name: str, obj):
        st.markdown(f"## {name}")
        streamlit_repr(obj)

    return st_display
