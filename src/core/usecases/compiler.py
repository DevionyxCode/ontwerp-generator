import xml.sax.saxutils as saxutils
from typing import Dict, Any

class DrawioUseCaseDiagramGenerator:
    def __init__(self):
        # Afmetingen
        self.actor_width, self.actor_height = 50, 100
        self.use_case_width, self.use_case_height = 220, 90
        self.padding_x = 30
        self.padding_y = 20
        self.title_height = 30

        # Systeemvak
        self.container_style = (
            "swimlane;fontStyle=1;startSize=30;fillColor=none;strokeColor=#000000;"
            "rounded=0;align=center;verticalAlign=top;"
        )

        # Usecase-ellips
        self.use_case_style = (
            "ellipse;whiteSpace=wrap;fillColor=#dae8fc;strokeColor=#6c8ebf;"
            "fontColor=#000000;align=center;verticalAlign=middle;"
        )

        # Relaties: zonder pijltjes
        self.relationship_style = "endArrow=none;html=1;rounded=0;"

    def _escape(self, text: str) -> str:
        return saxutils.escape(text, {"\"": "&quot;", "'": "&apos;"})

    def _create_cell(self, id_, x, y, w, h, text, style, parent=1):
        return (
            f'\n<mxCell id="{id_}" value="{self._escape(text)}" style="{style}" vertex="1" parent="{parent}">'
            f'\n<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>\n</mxCell>'
        )

    def _create_actor(self, id_, x, y, name):
        style = "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;"
        return self._create_cell(id_, x, y, self.actor_width, self.actor_height, name, style)

    def _create_edge(self, id_, source, target, points, style=None):
        edge_style = style if style else self.relationship_style
        xml = f'\n<mxCell id="{id_}" style="{edge_style}" edge="1" parent="1" source="{source}" target="{target}">'
        xml += '\n<mxGeometry relative="1" as="geometry">'
        if points:
            xml += '\n<Array as="points">'
            for x, y in points:
                xml += f'\n<mxPoint x="{x}" y="{y}"/>'
            xml += '\n</Array>'
        xml += '\n</mxGeometry>\n</mxCell>'
        return xml

    def run(self, json_data: Dict[str, Any]) -> str:
        actors = json_data.get("actors", [])
        use_cases = json_data.get("use_cases", [])
        relations = json_data.get("relations", [])
        system_name = json_data.get("system", "System")

        cell_id = 2
        header = '''<?xml version="1.0" encoding="UTF-8"?>
    <mxfile host="app.diagrams.net" agent="python-script" version="24.0.0" type="device">
    <diagram name="Use-Case Diagram" id="diagram1">
    <mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" connect="1"
     arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827"
     background="#FFFFFF" math="0" shadow="0">
    <root><mxCell id="0"/><mxCell id="1" parent="0"/>'''

        cells = []
        actor_map, usecase_map = {}, {}

        # Identificeer alle extend- en include-usecases zodat ze niet in de hoofdlijst komen
        exclude_ids = set()
        for uc in use_cases:
            exclude_ids.update(uc.get("extend", []))
            exclude_ids.update(uc.get("includes", []))

        # Alleen basis-usecases tekenen (dus geen extend of include)
        base_use_cases = [uc for uc in use_cases if uc['id'] not in exclude_ids]

        # Bereken maximale horizontale offset
        usecase_right_offset = 250
        max_offset = 0
        for uc in base_use_cases:
            num_extra = max(len(uc.get("includes", [])), len(uc.get("extend", [])))
            if num_extra > max_offset:
                max_offset = num_extra

        # Container positie en afmetingen
        container_x, container_y = 450, 100
        container_w = self.use_case_width + max_offset * usecase_right_offset + 2 * self.padding_x
        container_h = len(base_use_cases) * (
                    self.use_case_height + self.padding_y) + self.padding_y + self.title_height + 40
        container_id = str(cell_id)
        cells.append(
            self._create_cell(container_id, container_x, container_y, container_w, container_h, system_name,
                              self.container_style)
        )
        cell_id += 1

        # Actoren links
        num_actors = len(actors)
        if num_actors > 0:
            vertical_slot_height = container_h / num_actors
            actor_x = container_x - self.actor_width - self.padding_x - 200
            for i, actor in enumerate(actors):
                y_center = container_y + i * vertical_slot_height + vertical_slot_height / 2
                y = y_center - self.actor_height / 2
                actor_map[actor['id']] = str(cell_id)
                cells.append(self._create_actor(cell_id, actor_x, y, actor['name']))
                cell_id += 1

        # ---- Actor -> Actor relaties (linked_actors) ----
        for actor in actors:
            from_id = actor_map[actor['id']]
            for linked_id in actor.get('linked_actors', []):
                if linked_id in actor_map:
                    to_id = actor_map[linked_id]

                    from_idx = [a['id'] for a in actors].index(actor['id'])
                    to_idx = [a['id'] for a in actors].index(linked_id)

                    # Horizontale offset voor het kleine stukje links
                    line_offset = 20

                    # Begin links van de stickman
                    x_from = actor_x  # linkerzijde van de actor
                    y_from = container_y + from_idx * vertical_slot_height + vertical_slot_height / 2

                    # Eindpunt bij target actor (links)
                    x_to = actor_x  # linkerzijde van de target actor
                    y_to = container_y + to_idx * vertical_slot_height + vertical_slot_height / 2

                    # L-vormige lijn (stapjes)
                    points = [
                        (x_from - 10, y_from),  # klein horizontaal stukje naar links
                        (x_from - line_offset, y_from),  # horizontaal verder naar links
                        (x_from - line_offset, y_to),  # verticaal omhoog/omlaag naar y van target
                        (x_to - 10, y_to)  # horizontaal stukje naar target
                    ]

                    edge_style = "endArrow=blockThin;html=1;strokeColor=#000000;"
                    cells.append(self._create_edge(cell_id, from_id, to_id, points, style=edge_style))
                    cell_id += 1

        # Horizontaal gecentreerd midden in container
        start_x = (container_w - (self.use_case_width + max_offset * usecase_right_offset)) / 2
        start_y = self.title_height + self.padding_y // 2

        # Teken basis-usecases
        for i, uc in enumerate(base_use_cases):
            y = start_y + i * (self.use_case_height + self.padding_y)
            x = start_x
            parent_cell_id = cell_id
            usecase_map[uc['id']] = str(cell_id)
            cells.append(
                self._create_cell(cell_id, x, y, self.use_case_width, self.use_case_height, uc['name'],
                                  self.use_case_style, parent=container_id)
            )
            cell_id += 1

            # Include relaties
            for idx, inc_id in enumerate(uc.get("includes", [])):
                target_uc = next((u for u in use_cases if u['id'] == inc_id), None)
                if target_uc:
                    x_inc = x + (idx + 1) * usecase_right_offset
                    y_inc = y
                    inc_cell_id = cell_id
                    usecase_map[f"{uc['id']}_inc_{inc_id}"] = str(inc_cell_id)
                    cells.append(
                        self._create_cell(inc_cell_id, x_inc, y_inc, self.use_case_width, self.use_case_height,
                                          target_uc['name'], self.use_case_style, parent=container_id)
                    )
                    style_edge = "dashed=1;endArrow=blockThin;html=1;strokeColor=#000000;"
                    cells.append(self._create_edge(cell_id + 1000, parent_cell_id, inc_cell_id, [], style_edge))
                    cell_id += 1

            # Extend relaties
            for idx, ext_id in enumerate(uc.get("extend", [])):
                target_uc = next((u for u in use_cases if u['id'] == ext_id), None)
                if target_uc:
                    x_ext = x + (idx + 1) * usecase_right_offset
                    y_ext = y
                    ext_cell_id = cell_id
                    usecase_map[f"{uc['id']}_ext_{ext_id}"] = str(ext_cell_id)
                    cells.append(
                        self._create_cell(ext_cell_id, x_ext, y_ext, self.use_case_width, self.use_case_height,
                                          target_uc['name'], self.use_case_style, parent=container_id)
                    )
                    style_edge = "dashed=1;endArrow=blockThin;html=1;strokeColor=#000000;"
                    cells.append(self._create_edge(cell_id + 1000, parent_cell_id, ext_cell_id, [], style_edge))
                    cell_id += 1

        # Actor -> usecase relaties
        for rel in relations:
            if rel['actor_id'] in actor_map and rel['use_case_id'] in usecase_map:
                actor_id = actor_map[rel['actor_id']]
                usecase_id = usecase_map[rel['use_case_id']]

                actor_idx = [a['id'] for a in actors].index(rel['actor_id'])
                y_center = container_y + actor_idx * vertical_slot_height + vertical_slot_height / 2
                actor_y_center = y_center
                actor_x_right = actor_x + self.actor_width

                uc_idx = [uc['id'] for uc in use_cases].index(rel['use_case_id'])
                usecase_y_center = container_y + start_y + uc_idx * (
                            self.use_case_height + self.padding_y) + self.use_case_height // 2
                usecase_x_left = container_x + start_x

                mid_x = (actor_x_right + usecase_x_left) // 2
                points = [
                    (actor_x_right + 10, actor_y_center),
                    (mid_x, usecase_y_center),
                    (usecase_x_left, usecase_y_center)
                ]
                cells.append(self._create_edge(cell_id, actor_id, usecase_id, points))
                cell_id += 1

        footer = '\n</root></mxGraphModel></diagram></mxfile>'
        return header + "".join(cells) + footer
