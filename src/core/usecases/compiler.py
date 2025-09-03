import json
import math
import xml.sax.saxutils as saxutils
from typing import List, Dict, Any, Tuple


class DrawioUseCaseDiagramGenerator:
    """
    Genereert een Draw.io XML-bestand voor een use-case diagram.
    """

    def __init__(self):
        self.actor_width, self.actor_height = 80, 100
        self.use_case_width, self.use_case_height = 160, 80
        self.padding = 80
        self.actor_x = 50
        self.use_case_x_start = self.actor_x + self.actor_width + self.padding * 2
        self.container_style = "swimlane;fontStyle=0;childLayout=stackLayout;horizontal=1;startSize=30;horizontalStack=0;resizeParent=1;resizeParentCheck=0;collapsible=0;marginBottom=0;html=1;"
        self.actor_style = "umlActor;verticalLabelPosition=bottom;html=1;verticalAlign=top;strokeColor=#000000;fillColor=#FFFFFF;rounded=0;"
        self.use_case_style = "html=1;ellipse;whiteSpace=wrap;fillColor=#dae8fc;strokeColor=#6c8ebf;fontColor=#000000;verticalAlign=middle;align=center;"
        self.relationship_styles = {
            "default": "edgeStyle=orthogonalEdgeStyle;html=1;rounded=0;endArrow=open;dashed=0;endFill=0;",
            "includes": "edgeStyle=orthogonalEdgeStyle;html=1;rounded=0;dashed=1;endArrow=open;endFill=0;dashed=1;labelBackgroundColor=#ffffff;spacingTop=5;",
            "extends": "edgeStyle=orthogonalEdgeStyle;html=1;rounded=0;dashed=1;endArrow=open;endFill=0;dashed=1;labelBackgroundColor=#ffffff;spacingTop=5;"
        }

    def _escape(self, text: str) -> str:
        return saxutils.escape(text, {"\"": "&quot;", "'": "&apos;"})

    def _create_cell(self, id_: int, x: int, y: int, w: int, h: int, text: str, style: str, parent: int) -> str:
        return f'\n<mxCell id="{id_}" value="{self._escape(text)}" style="{style}" vertex="1" parent="{parent}">\n<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" />\n</mxCell>'

    def _create_edge(self, id_: int, source: str, target: str, label: str, style: str) -> str:
        return f'\n<mxCell id="{id_}" value="{label}" style="{style}" edge="1" parent="1" source="{source}" target="{target}">\n<mxGeometry relative="1" as="geometry" />\n</mxCell>'

    def run(self, json_data: Dict[str, Any]) -> str:
        """Hoofdfunctie om de volledige Draw.io XML te genereren."""
        actors = json_data.get("actors", [])
        use_cases = json_data.get("use_cases", [])
        relations = json_data.get("relations", [])
        system_name = json_data.get("system", "Use-Case Diagram")

        # Start Cell ID counter, 0 and 1 are reserved.
        cell_id = 2

        header = '''<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" agent="python-script-v3" version="24.0.0" type="device">
<diagram name="Use-Case Diagram" id="diagram1">
<mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" background="#FFFFFF" math="0" shadow="0">
<root><mxCell id="0"/><mxCell id="1" parent="0"/>'''

        cells_xml = []
        actor_map = {}
        use_case_map = {}

        # Determine total height for container and calculate layout
        # (calculations remain correct, no need to change)
        total_use_case_height = len(use_cases) * self.use_case_height + (len(use_cases) - 1) * self.padding + 40
        container_y = self.padding
        container_w = self.use_case_width * math.ceil(math.sqrt(len(use_cases))) + self.padding * (
                math.ceil(math.sqrt(len(use_cases))) - 1) + 40
        container_h = total_use_case_height

        # 1. Create container cell and increment ID
        container_id = cell_id
        cells_xml.append(
            self._create_cell(container_id, self.use_case_x_start - 20, container_y, container_w, container_h,
                              system_name, self.container_style, 1))
        cell_id += 1

        # 2. Create actor cells and increment ID for each
        actor_y = container_y
        for actor in actors:
            actor_map[actor['id']] = str(cell_id)
            cells_xml.append(self._create_cell(cell_id, self.actor_x, actor_y, self.actor_width, self.actor_height,
                                               actor['name'], self.actor_style, 1))
            actor_y += self.actor_height + self.padding
            cell_id += 1

        # 3. Create use case cells inside the container and increment ID for each
        use_case_y_offset = 30
        cols = math.ceil(math.sqrt(len(use_cases)))
        for i, use_case in enumerate(use_cases):
            col = i % cols
            row = i // cols
            x = 20 + col * (self.use_case_width + self.padding)
            y = use_case_y_offset + row * (self.use_case_height + self.padding)
            use_case_map[use_case['id']] = str(cell_id)
            cells_xml.append(self._create_cell(cell_id, x, y, self.use_case_width, self.use_case_height,
                                               use_case['name'], self.use_case_style, container_id))
            cell_id += 1

        # 4. Create relationships (edges) and increment ID for each
        for rel in relations:
            actor_id = rel.get("actor_id")
            use_case_id = rel.get("use_case_id")
            if actor_id in actor_map and use_case_id in use_case_map:
                cells_xml.append(self._create_edge(cell_id, actor_map[actor_id], use_case_map[use_case_id], "",
                                                   self.relationship_styles["default"]))
                cell_id += 1

        # 5. Create include/extend relationships (edges) and increment ID for each
        for uc in use_cases:
            if 'includes' in uc:
                for included_uc_id in uc['includes']:
                    if uc['id'] in use_case_map and included_uc_id in use_case_map:
                        cells_xml.append(
                            self._create_edge(cell_id, use_case_map[uc['id']], use_case_map[included_uc_id],
                                              "&lt;&lt;include&gt;&gt;", self.relationship_styles["includes"]))
                        cell_id += 1
            if 'extends' in uc:
                for extended_uc_id in uc['extends']:
                    if uc['id'] in use_case_map and extended_uc_id in use_case_map:
                        cells_xml.append(
                            self._create_edge(cell_id, use_case_map[uc['id']], use_case_map[extended_uc_id],
                                              "&lt;&lt;extend&gt;&gt;", self.relationship_styles["extends"]))
                        cell_id += 1

        # Footer of the XML
        footer = '''\n</root></mxGraphModel></diagram></mxfile>'''
        return header + "".join(cells_xml) + footer

