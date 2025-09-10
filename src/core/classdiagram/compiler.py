import xml.sax.saxutils as saxutils
from typing import List, Dict, Any, Tuple
import math

class DrawioClassDiagramGenerator:
    def __init__(self, padding: int = 100, class_width: int = 220):
        self.padding = padding
        self.class_width = class_width
        self.classes_input: List[Dict[str, Any]] = []
        self.colors = [
            "#FF0000", "#00AA00", "#0000FF", "#FFAA00",
            "#00AAAA", "#AA00AA", "#000000", "#AAAAAA",
        ]
        self.used_points = {
            "left_x": set(),
            "right_x": set(),
            "bridge_y": set()
        }


    def _escape(self, text: str) -> str:
        return saxutils.escape(text, {"\"": "&quot;", "'": "&apos;"})

    def _create_class_cell(self, cls: Dict[str, Any], x: int, y: int, cell_id: int) -> Tuple[str, int, Dict]:
        line_h = 22
        title_h = 40
        separator_h = 1

        attr_h = max(25, len(cls.get("attributes", [])) * line_h)
        meth_h = max(25, len(cls.get("methods", [])) * line_h)
        total_h = title_h + separator_h + attr_h + separator_h + meth_h + 10

        container_style = "whiteSpace=wrap;html=1;strokeColor=#000000;fillColor=#FFFFFF;"
        title_style = "text;align=center;verticalAlign=middle;fontSize=18;fontStyle=1;color=#000000;whiteSpace=wrap;html=1;"
        member_style = "text;align=left;verticalAlign=middle;fontSize=16;color=#000000;whiteSpace=wrap;html=1;"
        separator_style = "line;strokeWidth=1;strokeColor=#000000;"

        cells = []

        # container
        cells.append(
            f'<mxCell id="{cell_id}" value="" style="{container_style}" vertex="1" parent="1">'
            f'<mxGeometry x="{x}" y="{y}" width="{self.class_width}" height="{total_h}" as="geometry"/>'
            f'</mxCell>'
        )
        container_id = cell_id
        cell_id += 1

        # title
        cells.append(
            f'<mxCell id="{cell_id}" value="{self._escape(cls["name"])}" style="{title_style}" vertex="1" parent="{container_id}">'
            f'<mxGeometry x="0" y="0" width="{self.class_width}" height="{title_h}" as="geometry"/>'
            f'</mxCell>'
        )
        cell_id += 1

        # line under title
        cells.append(
            f'<mxCell id="{cell_id}" value="" style="{separator_style}" vertex="1" parent="{container_id}">'
            f'<mxGeometry x="0" y="{title_h}" width="{self.class_width}" height="{separator_h}" as="geometry"/>'
            f'</mxCell>'
        )
        cell_id += 1

        # attributes
        for i, attr in enumerate(cls.get("attributes", [])):
            cells.append(
                f'<mxCell id="{cell_id}" value="{self._escape(attr)}" style="{member_style}" vertex="1" parent="{container_id}">'
                f'<mxGeometry x="0" y="{title_h + separator_h + i*line_h}" width="{self.class_width}" height="{line_h}" as="geometry"/>'
                f'</mxCell>'
            )
            cell_id += 1

        # line under attributes
        cells.append(
            f'<mxCell id="{cell_id}" value="" style="{separator_style}" vertex="1" parent="{container_id}">'
            f'<mxGeometry x="0" y="{title_h + separator_h + attr_h}" width="{self.class_width}" height="{separator_h}" as="geometry"/>'
            f'</mxCell>'
        )
        cell_id += 1

        # methods
        for i, method in enumerate(cls.get("methods", [])):
            cells.append(
                f'<mxCell id="{cell_id}" value="{self._escape(method)}" style="{member_style}" vertex="1" parent="{container_id}">'
                f'<mxGeometry x="0" y="{title_h + 2*separator_h + attr_h + i*line_h}" width="{self.class_width}" height="{line_h}" as="geometry"/>'
                f'</mxCell>'
            )
            cell_id += 1

        class_data = {
            "id": cls["id"],
            "pos": (x, y),
            "width": self.class_width,
            "height": total_h,
            "container_id": container_id
        }

        return "\n".join(cells), cell_id, class_data

    def _generate_layout(self) -> Tuple[List[Dict[str, Any]], int]:
        classes_info = []
        cell_id = 2
        total_classes = len(self.classes_input)
        if total_classes == 0:
            return classes_info, cell_id

        columns = math.ceil(math.sqrt(total_classes))
        row_heights = [0] * math.ceil(total_classes / columns)

        temp_classes = []
        for cls in self.classes_input:
            xml, cell_id, class_data = self._create_class_cell(cls, 0, 0, cell_id)
            class_data['xml'] = xml
            temp_classes.append(class_data)

        for idx, cls in enumerate(temp_classes):
            row = idx // columns
            row_heights[row] = max(row_heights[row], cls['height'])

        padding = self.padding
        col_gap = 100
        x_start, y_start = 20, 20
        y_offset = 150  # <<< voeg deze toe om alles iets lager te zetten
        x_offset = 150  # schuif alles iets naar rechts
        y = y_start + y_offset
        for row_idx in range(len(row_heights)):
            x = x_start + x_offset
            for col_idx in range(columns):
                class_idx = row_idx * columns + col_idx
                if class_idx >= total_classes:
                    break
                cls = temp_classes[class_idx]
                cls['pos'] = (x, y)
                xml_lines = cls['xml'].splitlines()
                for i, line in enumerate(xml_lines):
                    if f'<mxCell id="{cls["container_id"]}"' in line:
                        xml_lines[i] = line.replace(f'x="0"', f'x="{cls["pos"][0]}"') \
                            .replace(f'y="0"', f'y="{cls["pos"][1]}"')
                cls['xml'] = "\n".join(xml_lines)

                classes_info.append(cls)
                x += cls['width'] + col_gap
            y += row_heights[row_idx] + padding

        return classes_info, cell_id

    def _get_connection_points(self, cls):
        x, y = cls['pos']
        w, h = cls['width'], cls['height']
        return {
            'top': (x + w/2, y),
            'bottom': (x + w/2, y + h),
            'left': (x, y + h/2),
            'right': (x + w, y + h/2)
        }

    def _calculate_orthogonal_path(self, source_cls, target_cls, fk_name="FK", step=8):
        used_points = self.used_points
        gap = 40

        # Start- en eindpunten
        x0, y0 = self._get_connection_points(source_cls)['left']
        x1, y1 = self._get_connection_points(target_cls)['right']

        # --- Startpoint Y vrijmaken (WP1 = startpoint Y) ---
        while (x0, y0) in used_points.get("start_points", set()):
            print(f"[DEBUG] Start point ({x0},{y0}) in use, shifting up by {step}")
            y0 -= step
        used_points.setdefault("start_points", set()).add((x0, y0))

        # --- Linker X vrijmaken (WP1/2) ---
        left_x = int(x0 - gap)
        while left_x in used_points.get("left_x", set()) or left_x in used_points.get("right_x", set()):
            print(f"[DEBUG] left_x {left_x} in use, shifting left by {step}")
            left_x -= step
        used_points.setdefault("left_x", set()).add(left_x)

        # --- Rechter X vrijmaken (WP3/4) ---
        right_x = int(x1 + gap)
        while right_x in used_points.get("right_x", set()) or right_x in used_points.get("left_x", set()):
            print(f"[DEBUG] right_x {right_x} in use, shifting right by {step}")
            right_x += step
        used_points.setdefault("right_x", set()).add(right_x)

        # --- Brug Y vrijmaken (WP2/3) ---
        bridge_y = int(target_cls['pos'][1] - target_cls['height'] / 4)
        while bridge_y < 0 or bridge_y in used_points.get("bridge_y", set()):
            print(f"[DEBUG] bridge_y {bridge_y} in use or <0, shifting down by {step}")
            bridge_y += step
        used_points.setdefault("bridge_y", set()).add(bridge_y)

        # --- Endpoint Y vrijmaken (WP4 = endpoint Y) ---
        while (x1, y1) in used_points.get("end_points", set()):
            print(f"[DEBUG] End point ({x1},{y1}) in use, shifting down by {step}")
            y1 += step
        used_points.setdefault("end_points", set()).add((x1, y1))

        # --- Waypoints maken ---
        wp1 = (left_x, y0)  # WP1 = exact startpoint Y
        wp2 = (left_x, bridge_y)
        wp3 = (right_x, bridge_y)
        wp4 = (right_x, y1)  # WP4 = exact endpoint Y

        print(f"[{fk_name}] Final waypoints: WP1{wp1}, WP2{wp2}, WP3{wp3}, WP4{wp4}")
        return [wp1, wp2, wp3, wp4]

    def _generate_relation_cells(self, relations: List[Dict[str, Any]], classes_info: List[Dict[str, Any]],
                                 start_id: int) -> str:
        class_map = {c['id']: c for c in classes_info}
        cell_id = start_id
        relation_cells = []
        color_count = len(self.colors)

        for idx, rel in enumerate(relations):
            source_cls = class_map[rel["from"]]
            target_cls = class_map[rel["to"]]

            # --- bereken waypoints
            waypoints = self._calculate_orthogonal_path(source_cls, target_cls)

            # --- fictieve start en eind waypoints
            start_x = source_cls['pos'][0]  # exact linkerzijde van container
            start_y = waypoints[0][1]  # hoogte van WP1
            end_x = target_cls['pos'][0] + target_cls['width']  # rechterzijde van target container
            end_y = waypoints[-1][1]  # hoogte van WP4

            # volledige puntenlijst: start + originele waypoints + eind
            full_points = [(start_x, start_y)] + waypoints + [(end_x, end_y)]

            # genereer XML
            points_xml = "<Array as='points'>" + "".join(
                f'<mxPoint x="{x}" y="{y}"/>' for x, y in full_points
            ) + "</Array>"

            # Kies kleur
            color = self.colors[idx % color_count]

            # Stijl op basis van type relatie
            rtype = rel.get("type", "association")
            style = f"html=1;strokeWidth=2;strokeColor={color};"
            if rtype == "association":
                style += "endArrow=open;"
            elif rtype == "aggregation":
                style += "endArrow=none;startArrow=diamondThin;startFill=0;startSize=10;"
            elif rtype == "composition":
                style += "endArrow=none;startArrow=diamondThin;startSize=10;"
            elif rtype == "Inheritance":
                style += "endArrow=block;endFill=0;"
            elif rtype == "implementation":
                style += "endArrow=block;endFill=0;dashed=1;"
            elif rtype == "dependency":
                style += "endArrow=open;dashed=1;"

            # Creeer de edge
            relation_cells.append(
                f'<mxCell id="{cell_id}" style="{style}" edge="1" parent="1" '
                f'source="{source_cls["container_id"]}" target="{target_cls["container_id"]}">'
                f'<mxGeometry relative="1" as="geometry">{points_xml}</mxGeometry>'
                f'</mxCell>'
            )
            cell_id += 1

        return "\n".join(relation_cells)

    def run(self, json_data: Dict[str, Any]) -> str:
        self.classes_input = json_data.get("classes", [])
        layout_info, last_class_id = self._generate_layout()
        class_cells_xml = "\n".join(c['xml'] for c in layout_info)
        relationship_cells_xml = self._generate_relation_cells(json_data.get("relations", []), layout_info, last_class_id)

        header = '''<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net">
<diagram name="Class Diagram" id="diagram1">
<mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" background="#FFFFFF" math="0" shadow="0">
<root><mxCell id="0"/><mxCell id="1" parent="0"/>'''
        footer = '</root></mxGraphModel></diagram></mxfile>'

        return header + class_cells_xml + "\n" + relationship_cells_xml + footer
