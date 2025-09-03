import json
import math
import xml.sax.saxutils as saxutils
from typing import List, Dict, Any, Tuple


class DrawioClassDiagramGenerator:
    """
    Genereert een Draw.io XML-string voor een klassendiagram vanuit een JSON-input.
    Deze versie genereert een ongecomprimeerde XML-string.
    """

    def __init__(self, padding: int = 150, class_width: int = 240):
        self.padding = padding
        self.class_width = class_width
        self.classes_input: List[Dict[str, Any]] = []
        self.colors = ["#FF0000", "#00AA00", "#0000FF", "#FFAA00", "#00AAAA", "#AA00AA", "#000000"]
        self.container_style = "swimlane;fontStyle=0;childLayout=stackLayout;horizontal=1;startSize=30;horizontalStack=0;resizeParent=1;resizeParentCheck=0;collapsible=0;marginBottom=0;html=1;"
        self.title_style = "text;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;spacingLeft=4;spacingRight=4;overflow=hidden;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;rotatable=0;whiteSpace=wrap;html=1;fontStyle=1"
        self.member_style = "text;strokeColor=none;fillColor=none;align=left;verticalAlign=top;spacingLeft=4;spacingRight=4;overflow=hidden;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;rotatable=0;whiteSpace=wrap;html=1;"
        self.relationship_styles = {
            "inheritance": {"endArrow": "block", "endFill": "0", "startArrow": "none"},
            "composition": {"endArrow": "none", "endFill": "0", "startArrow": "diamond", "startFill": "1"},
            "aggregation": {"endArrow": "none", "endFill": "0", "startArrow": "diamond", "startFill": "0"},
            "association": {"endArrow": "open", "endFill": "0", "startArrow": "none"},
            "default": {"endArrow": "none", "endFill": "0", "startArrow": "none"},
        }
        self.relation_styles = {
            "inheritance": {"endArrow": "block", "endFill": "0", "startArrow": "none"},
            "composition": {"endArrow": "none", "endFill": "0", "startArrow": "diamond", "startFill": "1"},
            "aggregation": {"endArrow": "none", "endFill": "0", "startArrow": "diamond", "startFill": "0"},
            "association": {"endArrow": "open", "endFill": "0", "startArrow": "none"},
            "default": {"endArrow": "none", "endFill": "0", "startArrow": "none"},
        }

    def _escape(self, text: str) -> str:
        return saxutils.escape(text, {"\"": "&quot;", "'": "&apos;"})

    def _create_cell(self, id_: int, x: int, y: int, w: int, h: int, text: str, style: str) -> str:
        return f'\n    <mxCell id="{id_}" value="{self._escape(text)}" style="{style}" vertex="1" parent="1">\n      <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" />\n    </mxCell>'

    def _make_class_cell(self, json_data: Dict[str, Any], x: int, y: int, start_id: int) -> Tuple[
        str, int, int, int, Dict]:
        def format_members(members: List[Dict], is_method: bool = False) -> str:
            lines = []
            for member in members:
                access_map = {"public": "+", "private": "-", "protected": "#"}
                access = access_map.get(member.get("access", "private"), "-")
                if is_method:
                    params = ", ".join(member.get("parameters", []))
                    ret_type = member.get("return_type", "void")
                    line = f'{access} {member["name"]}({params}): {ret_type}'
                else:
                    line = f'{access} {member["name"]}: {member["type"]}'
                lines.append(self._escape(line))
            return "<br>".join(lines)

        attributes_str = format_members(json_data.get("attributes", []))
        methods_str = format_members(json_data.get("methods", []), is_method=True)
        line_h, min_comp_h, title_h, line_separator_h = 20, 25, 30, 1

        attr_h = max(min_comp_h, len(json_data.get("attributes", [])) * line_h)
        meth_h = max(min_comp_h, len(json_data.get("methods", [])) * line_h)
        total_h = title_h + attr_h + line_separator_h + meth_h

        cells, cell_id = [], start_id
        cells.append(self._create_cell(cell_id, x, y, self.class_width, total_h, "", self.container_style))
        container_id = cell_id
        cell_id += 1
        cells.append(self._create_cell(cell_id, x, y, self.class_width, title_h, json_data['name'], self.title_style))
        cell_id += 1
        cells.append(
            self._create_cell(cell_id, x, y + title_h, self.class_width, attr_h, attributes_str, self.member_style))
        cell_id += 1

        separator_style = "line;strokeWidth=1;html=1;fontStyle=1;align=center;verticalAlign=middle;"
        cells.append(self._create_cell(cell_id, x, y + title_h + attr_h, self.class_width, line_separator_h, "",
                                       separator_style))
        cell_id += 1

        cells.append(self._create_cell(cell_id, x, y + title_h + attr_h + line_separator_h, self.class_width, meth_h,
                                       methods_str,
                                       self.member_style))
        cell_id += 1

        class_data = {"name": json_data['name'], "pos": (x, y), "width": self.class_width, "height": total_h,
                      "json": json_data, "container_id": container_id}
        return "\n".join(cells), cell_id, self.class_width, total_h, class_data

    def _generate_diagram_layout(self) -> Tuple[List[Dict[str, Any]], int]:
        if not self.classes_input: return [], 2

        total_classes = len(self.classes_input)
        columns = math.ceil(math.sqrt(total_classes))

        row_max_heights = {}
        for i, class_json in enumerate(self.classes_input):
            row = i // columns
            attr_h = max(25, len(class_json.get("attributes", [])) * 20)
            meth_h = max(25, len(class_json.get("methods", [])) * 20)
            class_h = 30 + attr_h + 1 + meth_h
            if row not in row_max_heights or class_h > row_max_heights[row]:
                row_max_heights[row] = class_h

        y_positions = []
        current_y = 0
        for row in range(math.ceil(total_classes / columns)):
            y_positions.append(current_y)
            current_y += row_max_heights.get(row, 0) + self.padding

        cell_id, classes_info = 2, []
        for i, class_json in enumerate(self.classes_input):
            col, row = i % columns, i // columns
            x = col * (self.class_width + self.padding)
            y = y_positions[row]

            xml, next_id, w, h, data = self._make_class_cell(class_json, x, y, cell_id)
            data['xml'] = xml
            classes_info.append(data)
            cell_id = next_id

        return classes_info, cell_id

    def _generate_relationship_cells(self, classes_info: List[Dict[str, Any]], start_cell_id: int) -> str:
        class_map = {c["name"]: c for c in classes_info}
        cell_id = start_cell_id
        relation_cells, rel_idx = [], 0

        used_waypoints_x = set()
        used_waypoints_y = set()

        def get_unique_x(x: float) -> float:
            offset = 0
            original_x = x
            while x in used_waypoints_x:
                offset += 15
                x = original_x - offset
            used_waypoints_x.add(x)
            return x

        def get_unique_y(y: float) -> float:
            offset = 0
            original_y = y
            while y in used_waypoints_y:
                offset += 10
                y = original_y + offset
            used_waypoints_y.add(y)
            return y

        for source_info in classes_info:
            for rel in source_info["json"].get("relationships", []):
                target_name = rel.get("target")
                if not target_name or target_name not in class_map: continue

                target_info = class_map[target_name]
                style_props = self.relation_styles.get(rel.get("type"), self.relation_styles["default"])

                source_x, source_y = source_info["pos"][0], source_info["pos"][1]
                target_x, target_y = target_info["pos"][0], target_info["pos"][1]

                source_mid_x = source_x + source_info["width"] / 2
                source_mid_y = source_y + source_info["height"] / 2
                target_mid_x = target_x + target_info["width"] / 2
                target_mid_y = target_y + target_info["height"] / 2

                source_point = (source_x + source_info["width"], source_mid_y) if source_x < target_x else (source_x,
                                                                                                            source_mid_y)
                target_point = (target_x, target_mid_y) if source_x < target_x else (target_x + target_info["width"],
                                                                                     target_mid_y)

                points = []
                if abs(source_x - target_x) < 50:
                    points.append(f'<mxPoint x="{source_point[0]}" y="{source_point[1]}" />')
                    points.append(f'<mxPoint x="{target_point[0]}" y="{target_point[1]}" />')
                else:
                    wp_x1 = get_unique_x(source_point[0] + self.padding / 2)
                    wp_x2 = get_unique_x(target_point[0] - self.padding / 2)
                    wp_y = get_unique_y(min(source_y, target_y) - self.padding / 4)

                    points.append(f'<mxPoint x="{source_point[0]}" y="{source_point[1]}" />')
                    points.append(f'<mxPoint x="{wp_x1}" y="{source_point[1]}" />')
                    points.append(f'<mxPoint x="{wp_x1}" y="{wp_y}" />')
                    points.append(f'<mxPoint x="{wp_x2}" y="{wp_y}" />')
                    points.append(f'<mxPoint x="{wp_x2}" y="{target_point[1]}" />')
                    points.append(f'<mxPoint x="{target_point[0]}" y="{target_point[1]}" />')

                color = self.colors[rel_idx % len(self.colors)]
                line_style = f"edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor={color};strokeWidth=2;"
                line_style += "".join(f"{k}={v};" for k, v in style_props.items())
                line_style += f"sourceLabel={self._escape(rel.get('source_multiplicity', ''))};targetLabel={self._escape(rel.get('target_multiplicity', ''))};"

                points_xml = f'<Array as="points">\n{"".join(points)}\n</Array>' if points else ""

                source_container_id = source_info["container_id"]
                target_container_id = target_info["container_id"]

                relation_cells.append(f'''
                <mxCell id="{cell_id}" style="{line_style}" edge="1" parent="1" source="{source_container_id}" target="{target_container_id}">
                  <mxGeometry relative="1" as="geometry">
                    {points_xml}
                  </mxGeometry>
                </mxCell>''')
                cell_id += 1
                rel_idx += 1

        return "\n".join(relation_cells)

    def run(self, json_data: List[Dict[str, Any]]) -> str:
        """
        Hoofdfunctie om de volledige Draw.io XML-string te genereren en terug te sturen.
        """
        self.classes_input = json_data
        layout_info, last_class_cell_id = self._generate_diagram_layout()
        class_cells_xml = "\n".join(c['xml'] for c in layout_info)
        relationship_cells_xml = self._generate_relationship_cells(layout_info, last_class_cell_id)

        header = '''<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" agent="python-script-v3" version="24.0.0" type="device">
<diagram name="Class Diagram" id="diagram1">
<mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" background="#FFFFFF" math="0" shadow="0">
<root><mxCell id="0"/><mxCell id="1" parent="0"/>'''
        footer = '''</root></mxGraphModel></diagram></mxfile>'''

        full_xml = header + class_cells_xml + "\n" + relationship_cells_xml + footer

        return full_xml


if __name__ == "__main__":
    json_string = """
    [
      { "name": "Person", "attributes": [{"name": "name", "type": "String", "access": "protected"}]},
      { "name": "Customer", "attributes": [{"name": "customerId", "type": "int", "access": "private"}], "methods": [{"name": "placeOrder", "return_type": "Order", "access": "public"}], "relationships": [{"type": "inheritance", "target": "Person"}]},
      { "name": "Order", "attributes": [{"name": "orderId", "type": "int", "access": "private"}], "relationships": [{"type": "association", "target": "Customer", "source_multiplicity": "*", "target_multiplicity": "1"}, {"type": "composition", "target": "OrderLine", "source_multiplicity": "1", "target_multiplicity": "1..*"}]},
      { "name": "OrderLine", "attributes": [{"name": "quantity", "type": "int", "access": "private"}], "relationships": [{"type": "aggregation", "target": "Product", "source_multiplicity": "*", "target_multiplicity": "1"}]},
      { "name": "Product", "attributes": [{"name": "productId", "type": "int", "access": "private"}]}
    ]
    """
    class_diagram_json = json.loads(json_string)

    generator = DrawioClassDiagramGenerator()
    drawio_xml_string = generator.run(class_diagram_json)

    output_filename = "class_diagram_string_output.drawio"
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(drawio_xml_string)
        print(f"✅ Succesvol '{output_filename}' gegenereerd. De output is een ongecomprimeerde XML-string.")
    except IOError as e:
        print(f"❌ Fout bij het schrijven naar het bestand: {e}")