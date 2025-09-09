import json
import xml.sax.saxutils as saxutils
from typing import Dict, Any

class DrawioUseCaseDiagramGenerator:
    """
    Genereert een Draw.io XML-bestand voor een use-case diagram
    met systeemvak, verticaal geplaatste usecases en stickman-acteurs links.
    """

    def __init__(self):
        self.actor_width, self.actor_height = 30, 60  # stickman grootte
        self.use_case_width, self.use_case_height = 160, 80
        self.padding = 40
        self.container_style = (
            "swimlane;fontStyle=0;childLayout=stackLayout;horizontal=1;"
            "startSize=30;horizontalStack=0;resizeParent=1;resizeParentCheck=0;"
            "collapsible=0;marginBottom=0;html=1;"
        )
        self.use_case_style = (
            "html=1;ellipse;whiteSpace=wrap;fillColor=#dae8fc;"
            "strokeColor=#6c8ebf;fontColor=#000000;verticalAlign=middle;align=center;"
        )
        self.relationship_style = "edgeStyle=orthogonalEdgeStyle;html=1;rounded=0;endArrow=open;dashed=0;endFill=0;"

    def _escape(self, text: str) -> str:
        return saxutils.escape(text, {"\"": "&quot;", "'": "&apos;"})

    def _create_cell(self, id_: int, x: int, y: int, w: int, h: int, text: str, style: str, parent: int) -> str:
        return f'\n<mxCell id="{id_}" value="{self._escape(text)}" style="{style}" vertex="1" parent="{parent}">' \
               f'\n<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" />\n</mxCell>'

    def _create_actor(self, id_: int, x: int, y: int, name: str) -> str:
        style = "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;"
        return self._create_cell(id_, x, y, self.actor_width, self.actor_height, name, style, 1)

    def _create_edge(self, id_: int, source: str, target: str, label: str) -> str:
        return f'\n<mxCell id="{id_}" value="{label}" style="{self.relationship_style}" edge="1" parent="1" source="{source}" target="{target}">' \
               f'\n<mxGeometry relative="1" as="geometry" />\n</mxCell>'

    def run(self, json_data: Dict[str, Any]) -> str:
        actors = json_data.get("actors", [])
        use_cases = json_data.get("use_cases", [])
        relations = json_data.get("relations", [])
        system_name = json_data.get("system", "Use-Case Diagram")

        cell_id = 2

        # Header XML
        header = '''<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" agent="python-script" version="24.0.0" type="device">
<diagram name="Use-Case Diagram" id="diagram1">
<mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" background="#FFFFFF" math="0" shadow="0">
<root><mxCell id="0"/><mxCell id="1" parent="0"/>'''

        cells_xml = []
        actor_map = {}
        use_case_map = {}

        # --- Systeemvak ---
        container_x = 150
        container_y = 50
        container_w = self.use_case_width + 2 * self.padding
        container_h = len(use_cases) * (self.use_case_height + self.padding) + self.padding
        container_id = cell_id
        cells_xml.append(self._create_cell(container_id, container_x, container_y, container_w, container_h,
                                           system_name, self.container_style, 1))
        cell_id += 1

        # --- Usecases ---
        for i, uc in enumerate(use_cases):
            x = container_x + self.padding
            y = container_y + self.padding + i * (self.use_case_height + self.padding)
            use_case_map[uc['id']] = str(cell_id)
            cells_xml.append(self._create_cell(cell_id, x, y, self.use_case_width, self.use_case_height,
                                               uc['name'], self.use_case_style, container_id))
            cell_id += 1

        # --- Actors links van systeemvak ---
        total_actor_height = len(actors) * (self.actor_height + self.padding) - self.padding
        actor_start_y = container_y + (container_h - total_actor_height) // 2
        actor_x = container_x - self.actor_width - self.padding

        for i, actor in enumerate(actors):
            y = actor_start_y + i * (self.actor_height + self.padding)
            cells_xml.append(self._create_actor(cell_id, actor_x, y, actor['name']))
            actor_map[actor['id']] = str(cell_id)
            cell_id += 1

        # --- Associations ---
        for rel in relations:
            a_id = rel['actor_id']
            uc_id = rel['use_case_id']
            if a_id in actor_map and uc_id in use_case_map:
                cells_xml.append(self._create_edge(cell_id, actor_map[a_id], use_case_map[uc_id], ""))
                cell_id += 1

        footer = '\n</root></mxGraphModel></diagram></mxfile>'
        return header + "".join(cells_xml) + footer
