from io import BytesIO

import pandas as pd
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa


def export_xlsx(dataframe: pd.DataFrame):
    with BytesIO() as b:
        writer = pd.ExcelWriter(b, engine="xlsxwriter")
        dataframe.to_excel(writer)
    return b


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type="application/pdf")
    return None
