import base64
from io import BytesIO
import json
import os

from PIL import Image, ImageFont
import numpy as np
from weasyprint import CSS, HTML
from weasyprint.text.fonts import FontConfiguration

from config.settings.base import STATIC_ROOT


def plt_get_text_width_pixel(text, fontsize=None):
    if fontsize is None:
        fontsize = 10

    font = ImageFont.load_default()
    _, _, w, _ = font.getbbox(str(text))
    return w


def get_data_columns_max_width(
    data, fontsize_content, fontsize_header, field_level_config={}, layout="horizontal"
):
    """
    get columns max width
    """
    column_names = list(data.columns)
    if type(data) is not np.ndarray:
        data = np.array(data)
    a = []
    if layout == "vertical":
        max_width = 1260
    else:
        max_width = 890
    for idx, cols in enumerate(data.T):
        if not field_level_config.get(column_names[idx]):
            m = max([plt_get_text_width_pixel(x, fontsize_content) for x in cols])
            m = max([m, plt_get_text_width_pixel(column_names[idx], fontsize_header)])
            max_w = min(m * 0.60, max_width)
            m = min([m, max_w])
            a.append(8 + m + 8)
        else:
            a.append(int(field_level_config[column_names[idx]]))
    return a


def generate_pdf_from_data(
    data,
    file_name,
    col_width={},
    rowHeights=40,
    header_bg_color="#000000",
    header_font_color="#FFFFFF",
    cell_bg_color="#FFFFFF",
    cell_font_color="#000000",
    logo={},
    layout="horizontal",
    header_font_size=10,
    content_font_size=10,
    column_alignment={},
    layout_embedded="horizontal",
    embedded_table_custom_layout=[],
):
    if layout == "vertical":
        if len(data) > 1:
            data = data.T.reset_index()
            df_col = data.columns.tolist()
            columns = ["Field"]

            for i in df_col:
                if i != "index":
                    columns.append(f"Value{str(i)}")
        else:
            data = data.T.reset_index()
            columns = ["Field", "Value"]
        data.columns = columns
    else:
        columns = data.columns.tolist()

    data_values = data.values.tolist()

    if not col_width.get("field_level_config"):
        if col_width.get("static_column_width"):
            col_width = [int(col_width["static_column_width"]) / 100] * len(columns)
        else:
            max_column_width = get_data_columns_max_width(
                data, content_font_size, header_font_size, layout=layout
            )
            col_width = [i * 1.2 / 100 for i in max_column_width]
    else:
        max_column_width = get_data_columns_max_width(
            data,
            content_font_size,
            header_font_size,
            field_level_config=col_width["field_level_config"],
            layout=layout,
        )
        col_width = [i * 1.2 / 100 for i in max_column_width]

    if layout == "horizontal":
        page_size = ((sum(col_width) + 9), 11)
    else:
        page_size = ((sum(col_width) + 3), 20)

    font_config = FontConfiguration()
    column_alignment_list = []
    if column_alignment:
        global_header_alignment = column_alignment["global_header"]
        global_content_alignment = column_alignment["global_content"]
        if column_alignment.get("field_level_config"):
            field_config = column_alignment["field_level_config"]
        else:
            field_config = {}
        for idx, i in enumerate(columns):
            if field_config.get(i):
                header_alignment = field_config[i]["header"]
                content_alignment = field_config[i]["content"]
            else:
                header_alignment = global_header_alignment
                content_alignment = global_content_alignment
            column_alignment_list.append([header_alignment, content_alignment])
    else:
        for idx, i in enumerate(columns):
            column_alignment_list.append(["center", "left"])

    page_html = "<div id='logo-container'></div>"

    _html = "<table style='height:100%;'><tr>"
    for col_idx, i in enumerate(columns):
        _html += f"<th style='font-weight:bold;background-color:{header_bg_color};color:{header_font_color};padding: 10px;font-size:{header_font_size}px; vertical-align: middle;width:{col_width[col_idx]}in;text-align:{column_alignment_list[col_idx][0]};'>{i}</th>"
    _html += "</tr>"
    for row_idx, row in enumerate(data_values):
        _html += "<tr class='rowElement'>"
        for col_idx, i in enumerate(row):
            if type(i) == str and i.startswith("[{"):
                data = json.loads(i)
                if (
                    not embedded_table_custom_layout
                    or (layout == "horizontal" and col_idx in embedded_table_custom_layout)
                    or (layout == "vertical" and row_idx in embedded_table_custom_layout)
                ):
                    ltype = "custom"
                else:
                    ltype = "default"
                if layout_embedded == "horizontal" or ltype == "default":
                    nested_table_html = "<table style='width:auto;'><tr>"
                    for n_col in data[0].keys():
                        nested_table_html += f"<th style='text-align:center;padding:10px;font-size:{content_font_size}px;vertical-align: middle;'>{n_col}</th>"
                    nested_table_html += "</tr>"
                    for nest_row in data:
                        nested_table_html += "<tr>"
                        for n_val in nest_row.values():
                            nested_table_html += f"<td style='text-align:{column_alignment_list[col_idx][1]};padding:5px;font-size:{content_font_size}px;vertical-align: middle;'>{str(n_val)}</td>"
                        nested_table_html += "</tr>"
                    nested_table_html += "</table>"
                    i = nested_table_html
                else:
                    nested_table_html = "<table style='width:auto;'><tr>"
                    nested_table_html += f"<th style='text-align:center;padding:5px;font-size:{content_font_size}px;vertical-align: middle;'>Field</th>"
                    nested_table_html += f"<th style='text-align:center;padding:5px;font-size:{content_font_size}px;vertical-align: middle;'>Value</th>"
                    nested_table_html += "</tr>"
                    for nest_row in data:
                        for ncol, n_val in nest_row.items():
                            nested_table_html += "<tr>"
                            nested_table_html += f"<td style='text-align:{column_alignment_list[col_idx][1]};padding:5px;font-size:{content_font_size}px;vertical-align: middle;'>{ncol}</td>"
                            nested_table_html += f"<td style='text-align:{column_alignment_list[col_idx][1]};padding:5px;font-size:{content_font_size}px;vertical-align: middle;'>{str(n_val)}</td>"
                            nested_table_html += "</tr>"
                    nested_table_html += "</table>"
                    i = nested_table_html
            else:
                pass
            _html += f"<td style='padding: 10px;color:{cell_font_color}; background-color:{cell_bg_color}; font-size:{content_font_size}px; vertical-align: middle;width:{col_width[col_idx]}in;text-align:{column_alignment_list[col_idx][1]};'>{str(i)}</td>"
        _html += "</tr>"
    page_html += _html
    rtf_html = HTML(string=page_html)
    css_string = """
    @page {
        padding: 0px;
        @bottom-right{
            content: "Page " counter(page) " of " counter(pages);
        }
    """
    div_css = ""

    if logo.get("add_logo") == "yes" and logo.get("file_name"):
        if os.path.exists(f"{logo['file_name']}"):
            temp_image = Image.open(logo["file_name"])
        else:
            page_html = page_html.replace(
                "<div id='logo-container'></div>",
                f"<div id='logo-container'><p style='position: absolute; top: 43px; font-size: 8px; font-family: Arial;'>No image found</p></div>",
            )
            temp_image = Image.open(f"{STATIC_ROOT}/images/Base_theme/cross.png")

        figfile = BytesIO()
        temp_image.save(figfile, format="png")
        temp_image.close()
        figfile.seek(0)
        figdata_png = figfile.getvalue()
        figdata_png = base64.b64encode(figdata_png)
        encoded_image = figdata_png.decode("utf8")
        logo_image = f"url('data:image/png;base64,{encoded_image}')"

        if logo.get("placement") == "top_left":
            css_string += """
            @top-left {content: element(top-left)}
            """
            div_css += f"""
            #logo-container {{
                position: running(top-left);
                height:60px;
                width:200px;
                background-image: {logo_image};
                background-repeat:no-repeat;
                background-position:left center;
                background-attachment:scroll;
                background-size:auto;
            }}
            """
        elif logo.get("placement") == "top_right":
            css_string += """
            @top-right {content: element(top-right)}
            """
            div_css += f"""
            #logo-container {{
                position: running(top-right);
                height:60px;
                width:200px;
                background-image: {logo_image};
                background-repeat:no-repeat;
                background-position:left center;
                background-attachment:scroll;
                background-size:auto;
            }}
            """
        elif logo.get("placement") == "bottom_left":
            css_string += """
            @bottom-left {content: element(bottom-left)}
            """
            div_css += f"""
            #logo-container {{
                position: running(bottom-left);
                height:60px;
                width:200px;
                background-image: {logo_image};
                background-repeat:no-repeat;
                background-position:left center;
                background-attachment:scroll;
                background-size:auto;
            }}
            """
        else:
            css_string += """
            @bottom-right {content: element(bottom-right)}
            @bottom-left {content: "Page " counter(page) " of " counter(pages);}
            """
            div_css += f"""
            #logo-container {{
                position: running(bottom-right);
                height:60px;
                width:200px;
                background-image: {logo_image};
                background-repeat:no-repeat;
                background-position:left center;
                background-attachment:scroll;
                background-size:auto;
            }}
            """

    else:
        pass
    css_string += f"size: {page_size[0]}in {page_size[1]}in !important;"
    css_string += """
    }"""
    css_string += div_css
    css_string += f"""
    table {{width: 100%;}}
    table {{font-family: Arial, Helvetica, sans-serif;}}
    table,th,td {{ border: 1px solid black; border-collapse: collapse;}}
    """
    css = CSS(string=css_string, font_config=font_config)
    rtf_html = HTML(string=page_html)
    rtf_html.write_pdf(file_name, stylesheets=[css], font_config=font_config)
    return file_name
