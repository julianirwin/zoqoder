from  nicegui import ui, app
import zoqoder as zq
from secrets_zotero import api_key
import asyncio

library_id = "5374742"

def html_coding_table():
    table_header = f"""
    <link rel="stylesheet" href="https://cdn.simplecss.org/simple.min.css">
    <h1>Coding Summary</h1>
    <table>
        <tr>
            <th>Keyword</th>
            <th>Approx. Page</th>
            <th>Context</th>
        </tr>
    """
    table_row = """
        <tr>
            <td>{keyword}</td>
            <td>{page}</td>
            <td>{context}</td>
        </tr>
    """
    table_rows = [table_row.format(keyword=k, page=p, context=c) for (k, c), p in zip(keywords_and_contexts, pages)]
    return table_header + "".join(table_rows) + "</table>"


zotero = None
def connect():
    global zotero
    try:
        zotero = zq.zotero_connect(
            library_id=library_id_input.value, 
            library_type=library_type_input.value,
            api_key=api_key_input.value)
        label_connected.set_text("Connected")
    except:
        label_connected.set_text("Connection Error")


all_annotations = None
async def load_highlights():
    global all_annotations
    all_annotations = await asyncio.to_thread(zq.all_highlights, zotero)
    label_num_highlights.set_text(f"Loaded {len(all_annotations)} highlights.")


def _annotation_fields():
    fields = []
    if cb_annotation_key.value:
        fields.append("key")
    if cb_text.value:
        fields.append("annotationText")
    if cb_comment.value:
        fields.append("annotationComment")
    if cb_color.value:  
        fields.append("annotationColor")
    if cb_tags.value:   
        fields.append("tags")
    return fields

def _document_fields():
    fields = []
    if cb_doc_key.value:
        fields.append("key")
    if cb_date.value:
        fields.append("date")
    if cb_creator.value:
        fields.append("creatorSummary")
    if cb_title.value:  
        fields.append("title")
    if cb_publication.value:   
        fields.append("publicationTitle")
    return fields


def generate_summary():
    table_header = """
    <table class="table-auto">
        <thead>
            <tr>
                {headers}
            </tr>
        </thead>
    """
    table_footer = """
    </table>"""
    doc_fields = _document_fields()
    annot_fields = _annotation_fields()
    unique_tags = zq.items_unique_tags(all_annotations)
    summary = zq.tabulate_coding_summary(
        zotero, 
        all_annotations, 
        document_fields=doc_fields, 
        annotation_fields=annot_fields)
    # raw_output.set_text(str(summary))
    columns = [*doc_fields, *unique_tags]
    headers = "\n".join(map(_surround_th, columns))
    table_rows = """
        <tbody>
    """
    for row_dict in summary:
        table_rows += "<tr>"
        row_values = [row_dict.get(c, "") for c in columns]
        table_rows += "\n".join(map(_surround_td, row_values))
        table_rows += "</tr>"
    table_rows += "</tbody>"
    html = (
        table_header.format(headers=headers) + 
        table_rows + 
        table_footer
    )
    html_output.set_content(html)

def _surround_th(s):
    return f'<th class="border"">{s}</th>' 

def _surround_td(s):
    return f'<td class="border">{s}</td>' 




with ui.row().classes("w-full"):
    with ui.row().classes("w-3/4 flex mx-auto"):
        switch_dark_mode = ui.switch("Dark Mode", value=True)
        ui.dark_mode().bind_value_from(switch_dark_mode)
    with ui.row().classes("w-3/4 flex mx-auto"):
        ui.label("Zoqoder GUI").classes("text-4xl font-bold")
    with ui.row().classes("w-3/4 mx-auto"):
        with ui.card():
            ui.label("Setup").classes("text-xl font-bold")
            api_key_input = ui.input("API Key", value=str(api_key))
            library_id_input = ui.input("Library ID", value=library_id)
            library_type_input = ui.select(options=["user", "group"], value="group")

            ui.button("Connect", on_click=connect)
            label_connected = ui.label("")

            ui.button("Load Highlights", on_click=load_highlights)
            label_num_highlights = ui.label("")

        with ui.card():
            ui.label("Annotation Fields").classes("text-xl font-bold")
            cb_annotation_key = ui.checkbox("Key", value=False)
            cb_text = ui.checkbox("Text", value=True)
            cb_comment = ui.checkbox("Comment", value=False)
            cb_color = ui.checkbox("Color", value=False)
            cb_tags = ui.checkbox("Tags", value=False)

        with ui.card():
            ui.label("Document Fields").classes("text-xl font-bold")
            cb_doc_key = ui.checkbox("Key", value=False)
            cb_date = ui.checkbox("Date", value=True)
            cb_creator = ui.checkbox("Creator Summary", value=True)
            cb_title = ui.checkbox("Title", value=True)
            cb_publication = ui.checkbox("Publication", value=False)

with ui.row().classes("w-full"):
    with ui.row().classes("w-3/4 mx-auto"):
        with ui.column():
            ui.button("Generate Summary", on_click=generate_summary)
            ui.label("Coding Summary").classes("text-4xl font-bold")
            raw_output = ui.label("")
    with ui.row().classes("w-3/4 mx-auto pb-16"):
        html_output = ui.html("")

ui.run()