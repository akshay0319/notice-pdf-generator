# app/core/pdf_engine.py

from weasyprint import HTML
from jinja2 import Template, Environment
from io import BytesIO

def render_pdf_from_html(html: str, output_stream):
    HTML(string=html).write_pdf(target=output_stream)

def compile_template(html_str: str):
    env = Environment()
    template = env.from_string(html_str)
    return template

def render_pdf_bytes(html: str) -> bytes:
    buffer = BytesIO()
    HTML(string=html).write_pdf(target=buffer)
    return buffer.getvalue()
