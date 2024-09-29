from io import BytesIO

import pandas as pd


def export_xlsx(dataframe: pd.DataFrame):
    with BytesIO() as b:
        writer = pd.ExcelWriter(b, engine="xlsxwriter")
        dataframe.to_excel(writer)
    return b
