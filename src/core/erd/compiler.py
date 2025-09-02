import json
import math
import xml.sax.saxutils as saxutils


class DrawioERDGenerator:
    def __init__(self, padding=100):
        self.padding = padding
        self.tables_input = []
        self.colors = [
            "#FF0000", "#00AA00", "#0000FF", "#FFAA00",
            "#00AAAA", "#AA00AA", "#000000", "#AAAAAA",
        ]

    def escape_text(self, text):
        return saxutils.escape(text, {"\"": "&quot;", "'": "&apos;"})

    def create_rectangle_cell(self, id_, x, y, w, h, text, style=None):
        if style is None:
            style = ("shape=rectangle;whiteSpace=wrap;html=1;"
                     "strokeColor=#000000;fillColor=#FFFFFF;fontSize=14;fontFamily=Arial;fontStyle=1")
        text_escaped = self.escape_text(text)
        return f'''
    <mxCell id="{id_}" value="{text_escaped}" style="{style}" vertex="1" parent="1">
      <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" />
    </mxCell>'''

    def make_table_drawio(self, json_data, start_x, start_y, start_id):
        col1_w, col2_w, row_h = 60, 320, 40
        rows = 1 + len(json_data["fields"])
        width, height = col1_w + col2_w, row_h * rows

        cells = []
        cell_id = start_id

        # Achtergrond
        cells.append(self.create_rectangle_cell(str(cell_id), start_x, start_y, width, height, ""))
        background_id = cell_id
        cell_id += 1

        title_style = ("shape=rectangle;whiteSpace=wrap;html=1;"
                       "strokeColor=#000000;fillColor=#FFFFFF;fontSize=16;fontFamily=Arial;fontStyle=1;")
        cells.append(self.create_rectangle_cell(str(cell_id), start_x, start_y, width, row_h, json_data['title'], title_style))
        title_id = cell_id
        cell_id += 1

        fields_cells = []
        for i, field in enumerate(json_data["fields"]):
            y = start_y + row_h * (i + 1)
            type_id = cell_id
            cells.append(self.create_rectangle_cell(str(cell_id), start_x, y, col1_w, row_h, field["type"]))
            cell_id += 1
            name_id = cell_id
            # Bouw veldbeschrijving
            desc = field["name"] + "\n" + field["datatype"]
            props = []
            if field.get("not_null", False):
                props.append("NOT NULL")
            if field.get("unique", False):
                props.append("UNIQUE")
            if props:
                desc += "\n" + ", ".join(props)

            cells.append(self.create_rectangle_cell(str(cell_id), start_x + col1_w, y, col2_w, row_h, desc))

            cell_id += 1
            fields_cells.append({
                "type": field["type"],
                "name": field["name"],
                "references": field.get("references"),
                "type_cell_id": type_id,
                "name_cell_id": name_id,
                "x": start_x,
                "y": y,
                "width_type": col1_w,
                "width_name": col2_w,
                "height": row_h,
            })

        # Verticale lijn
        line_style = "strokeColor=#000000;strokeWidth=2;endArrow=none;endFill=0;"
        vertical_line = f'''
    <mxCell id="{cell_id}" style="{line_style}" edge="1" parent="1">
      <mxGeometry relative="1" as="geometry">
        <mxPoint x="{start_x + col1_w}" y="{start_y + row_h}" as="sourcePoint" />
        <mxPoint x="{start_x + col1_w}" y="{start_y + height}" as="targetPoint" />
      </mxGeometry>
    </mxCell>'''
        cells.append(vertical_line)
        cell_id += 1

        table_data = {
            "background_id": background_id,
            "title_id": title_id,
            "fields_cells": fields_cells,
            "position": (start_x, start_y),
            "width": width,
            "height": height,
            "title": json_data['title'],
        }

        return "\n".join(cells), cell_id, width, height, table_data

    def make_multiple_tables_drawio(self):
        import logging
        logging.basicConfig(level=logging.DEBUG)
        import math

        total_tables = len(self.tables_input)
        columns = math.ceil(math.sqrt(total_tables))
        cells, cell_id, relation_idx = [], 2, 0
        tables_info, temp_tables = [], []

        for table_json in self.tables_input:
            _, next_id, w, h, data = self.make_table_drawio(table_json, 0, 0, start_id=cell_id)
            temp_tables.append({"json": table_json, "width": w, "height": h})
            cell_id = next_id

        y_positions, current_y = [], 0
        for row in range(math.ceil(total_tables / columns)):
            row_tables = temp_tables[row * columns:(row + 1) * columns]
            max_h = max(t["height"] for t in row_tables)
            y_positions.append(current_y)
            current_y += max_h + self.padding

        cell_id = 2
        for idx, t in enumerate(temp_tables):
            col, row = idx % columns, idx // columns
            x = col * (400 + self.padding)
            y = y_positions[row]

            table_cells, next_id, w, h, data = self.make_table_drawio(t["json"], x, y, cell_id)
            cells.append(table_cells)
            cell_id = next_id
            tables_info.append({"json": t["json"], "data": data, "pos": (x, y), "width": w, "height": h})

        table_map = {t["data"]["title"]: t for t in tables_info}
        relations_cells = []

        used_wp14_x = set()
        used_wp23_pairs = set()
        used_pk_y_per_field = {}

        def get_unique_x_wp14(x):
            offset = 0
            original_x = x
            while x in used_wp14_x:
                offset += 5
                x = original_x - offset
            used_wp14_x.add(x)
            return x, -offset

        def get_unique_wp23_y(y):
            offset = 0
            original_y = y
            while (y, y) in used_wp23_pairs:
                offset += 5
                y = original_y + offset
            used_wp23_pairs.add((y, y))
            return y

        for t in tables_info:
            for f in t["data"]["fields_cells"]:
                if f["type"] == "FK" and f["references"]:
                    ref_table_name = f["references"]["table"]
                    ref_field_name = f["references"]["field"]
                    if ref_table_name not in table_map:
                        continue

                    ref_table = table_map[ref_table_name]
                    ref_field = next((rf for rf in ref_table["data"]["fields_cells"] if rf["name"] == ref_field_name),
                                     None)
                    if not ref_field:
                        continue

                    # Vind het eigen veld in FK-tabel
                    own_field = next((field for field in t["json"]["fields"] if field["name"] == f["name"]), None)
                    is_unique = own_field.get("unique", False) if own_field else False
                    is_not_null = own_field.get("not_null", False) or own_field.get("not null",
                                                                                    False) if own_field else False

                    # === START_ARROW logica (FK-kant) ===
                    start_arrow = "ERzeroToMany"  # standaard

                    if is_unique:
                        start_arrow = "ERzeroToOne"


                    # === END_ARROW logica (PK-kant) ===
                    end_arrow = "ERzeroToOne"  # standaard
                    if is_not_null:
                        end_arrow = "ERmandOne"

                    # === Posities en punten voor pijlen ===
                    fk_x, fk_y = t["pos"][0], f["y"] + f["height"] / 2
                    pk_x, pk_y = ref_table["pos"][0], ref_field["y"] + ref_field["height"] / 2
                    half_pad = self.padding / 2

                    raw_wp1_x = f["x"] - half_pad
                    wp1_x, offset1 = get_unique_x_wp14(raw_wp1_x)
                    wp1_y = fk_y

                    raw_wp4_x = ref_field["x"] - half_pad
                    wp4_x, offset4 = get_unique_x_wp14(raw_wp4_x)
                    wp4_y = pk_y

                    key = (ref_table_name, ref_field_name)
                    if key not in used_pk_y_per_field:
                        used_pk_y_per_field[key] = set()

                    offset_y = 0
                    while (pk_y + offset_y) in used_pk_y_per_field[key]:
                        offset_y += 5

                    if offset_y > 0:
                        pk_y += offset_y
                        wp4_y += offset_y

                    used_pk_y_per_field[key].add(pk_y)

                    shared_y = get_unique_wp23_y(t["pos"][1] - half_pad)

                    wp2_x = t["pos"][0] - half_pad + offset1
                    wp2_y = shared_y

                    wp3_x = ref_table["pos"][0] - half_pad + offset4
                    wp3_y = shared_y

                    if t["pos"][0] != ref_table["pos"][0]:
                        points = f'''
                          <Array as="points">
                            <mxPoint x="{wp1_x}" y="{wp1_y}" />
                            <mxPoint x="{wp2_x}" y="{wp2_y}" />
                            <mxPoint x="{wp3_x}" y="{wp3_y}" />
                            <mxPoint x="{wp4_x}" y="{wp4_y}" />
                          </Array>'''
                    else:
                        wp4_x = wp1_x
                        points = f'''
                              <Array as="points">
                                <mxPoint x="{wp1_x}" y="{wp1_y}" />
                                <mxPoint x="{wp4_x}" y="{wp4_y}" />
                              </Array>'''

                    color = self.colors[relation_idx % len(self.colors)]
                    line_style = (
                        f"strokeColor={color};strokeWidth=2;endArrow={end_arrow};"
                        f"endFill=1;startArrow={start_arrow};startFill=0;"
                    )

                    relations_cells.append(f'''
                    <mxCell id="{cell_id}" style="{line_style}" edge="1" parent="1">
                      <mxGeometry relative="1" as="geometry">
                        <mxPoint x="{fk_x}" y="{fk_y}" as="sourcePoint" />{points}
                        <mxPoint x="{pk_x}" y="{pk_y}" as="targetPoint" />
                      </mxGeometry>
                    </mxCell>''')
                    cell_id += 1
                    relation_idx += 1

        return "\n".join(cells) + "\n" + "\n".join(relations_cells)

    def create_full_drawio_xml(self):
        header = '''<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" modified="2025-05-21T17:30:00.000Z" agent="python-script" etag="xyz" version="22.1.22" type="device">
  <diagram id="diagram1" name="Pagina-1">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>'''
        footer = '''
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''
        return header + self.make_multiple_tables_drawio() + footer

    def run(self, json):
        self.tables_input = json
        xml_content = self.create_full_drawio_xml()
        return xml_content



#relatie type te maken:

#als PK is one-to-many en unique en not null dan is de end arrow ERone
#als PK is one-to-many en niet unique en niet not null dan is de end arrow ERzeroToOne
#als PK is one-to-many en niet unique en niet not null en is FK unique dan is de end arrow ERzeroToOne en de start arrow ook ERzeroToOne
#als PK is one-to-many en niet unique en niet not null en is FK not null dan is de end arrow ERmandOne en de start arrow ook ERzeroToMany