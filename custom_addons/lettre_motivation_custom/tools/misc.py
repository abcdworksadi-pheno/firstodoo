# -*- coding: utf-8 -*-

from io import BytesIO
from base64 import b64decode
from datetime import datetime
from docx import Document
from docx.shared import Mm
from docxtpl import InlineImage, RichText
from bs4 import BeautifulSoup
from num2words import num2words
from babel.dates import format_date
from babel.numbers import format_currency

# Partial Function
def render_image(tpl, imgb64, width=None, height=None):
    """Render an image in the document"""
    width = Mm(width) if width else None
    height = Mm(height) if height else None
        
    if not imgb64:
        return ''

    image_stream = BytesIO(b64decode(imgb64))
    return InlineImage(
        tpl, image_descriptor=image_stream, width=width, height=height
    )
    
def render_html_as_subdoc(tpl, html_code=None):
    """Render HTML as a subdocument"""
    if not (
        isinstance(html_code, str)
        and bool(BeautifulSoup(html_code, "html.parser").find())
    ):
        return ""

    temp = BytesIO()
    desc_document = Document()
    from htmldocx import HtmlToDocx
    new_parser = HtmlToDocx()
    new_parser.add_html_to_document(html_code, desc_document)
    desc_document.save(temp)
    temp.seek(0)
    return tpl.new_subdoc(temp)


def add_new_subdoc(tpl, docx_file):
    """Add a new subdocument"""
    if docx_file:
        return tpl.new_subdoc(BytesIO(b64decode(docx_file)))
    
    return tpl.new_subdoc()


def replace_image(tpl, dummy_pic, imgb64):
    """Replace an image in the template"""
    if not imgb64:
        return ''

    tpl.replace_pic(dummy_pic, BytesIO(b64decode(imgb64)))
    return ''

def replace_media(tpl, dummy_pic, imgb64):
    """Replace media in the template"""
    if not imgb64:
        return ''

    tpl.replace_media(dummy_pic, BytesIO(b64decode(imgb64)))
    return ''

def replace_embedded(tpl, dummy_embeed, file_b64):
    """Replace embedded object in the template"""
    if not file_b64:
        return ''

    tpl.replace_embedded(dummy_embeed, BytesIO(b64decode(file_b64)))
    return ''

def replace_zipname(tpl, embedded_object_path, file_b64):
    """Replace zipname in the template"""
    if not file_b64:
        return ''

    tpl.replace_zipname(embedded_object_path, BytesIO(b64decode(file_b64)))
    return ''

# Formatting Function
def parse_html(html):
    """Parse HTML and return plain text"""
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()

def formatdate(date_required=datetime.today(), format="full", lang="fr_FR", **kwargs):
    """Format a date according to locale"""
    return format_date(date_required, format=format, locale=lang, **kwargs)

def spelled_out(number, lang="fr_FR", to="cardinal", **kwargs):
    """Spell out a number in words"""
    return num2words(number, lang=lang, to=to, **kwargs)

def convert_currency(number, currency_field, locale='fr_FR', **kwargs):
    """Convert a number to currency format"""
    currency_name = currency_field.name if hasattr(currency_field, 'name') else str(currency_field)
    return format_currency(number, currency_name, locale=locale, **kwargs)

def format_abs(number):
    """Return absolute value of a number"""
    return abs(number)

def rich_text(text, **kwargs):
    """Convert text to rich text format"""
    if not text:
        return ""
    
    return RichText(text, **kwargs)

