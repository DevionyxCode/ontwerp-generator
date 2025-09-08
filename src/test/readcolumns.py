from docx import Document

doc = Document("voorbeeld.docx")
tables_data = []

for table in doc.tables:
    table_matrix = []
    for row in table.rows:
        row_data = []
        for cell in row.cells:
            cell_dict = {
                "text": cell.text,
                # "bg_color": cell._tc.tcPr.shd.fill  # background color ophalen is mogelijk, maar iets complexer
            }
            row_data.append(cell_dict)
        table_matrix.append(row_data)
    tables_data.append(table_matrix)

print(tables_data)
