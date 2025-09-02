import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font, Alignment
from io import BytesIO


class ScrumboardExcelExporter:
    def __init__(self, scrumboard):
        """
        Initialiseer de exporter.
        :param scrumboard: dict van columns en blokken
        """
        self.scrumboard = scrumboard

    def prepare_data(self):
        """Zet de scrumboard dict om naar een DataFrame met kolommen als board kolommen."""
        max_len = max(len(tasks) for tasks in self.scrumboard.values())
        data = {col: [] for col in self.scrumboard.keys()}

        for i in range(max_len):
            for col, tasks in self.scrumboard.items():
                if i < len(tasks):
                    task = tasks[i]
                    content = (
                        f"ID: {task['id']}\n"
                        f"Titel: {task['title']}\n"
                        f"Content: {task['content']}\n"
                        f"Prioriteit: {task['priority']}\n"
                        f"Tijd: {task['time_estimate']}\n"
                        f"Assignee: {task['assignee']}\n"
                        f"Tags: {', '.join(task['tags'])}\n"
                        f"Gemaakt: {task['created_at']}\n"
                        f"Laatst Update: {task['updated_at']}"
                    )
                    data[col].append(content)
                else:
                    data[col].append("")
        self.df = pd.DataFrame(data)

    def save_to_bytes(self):
        """Sla de DataFrame op in-memory als Excel en return bytes."""
        # Schrijf eerst DataFrame naar BytesIO
        with BytesIO() as buffer:
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                self.df.to_excel(writer, index=False)
                writer._save()

            buffer.seek(0)
            # Openen met openpyxl voor styling
            wb = load_workbook(buffer)
            ws = wb.active

            # Header stijl
            header_fill = PatternFill(start_color="4B6CB7", end_color="4B6CB7", fill_type="solid")
            header_font = Font(color="FFFFFF", bold=True)
            for cell in ws[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center", vertical="center")

            # Bereken maximale breedte over alle kolommen
            max_col_width = 0
            for col in ws.columns:
                for cell in col:
                    if cell.value:
                        max_col_width = max(max_col_width, max(len(str(line)) for line in str(cell.value).split("\n")))

            # Zet dezelfde breedte voor alle kolommen + wrap text
            for col in ws.columns:
                col_letter = col[0].column_letter
                ws.column_dimensions[col_letter].width = max_col_width + 5
                for cell in col:
                    cell.alignment = Alignment(wrap_text=True, vertical="top")

            # Opslaan opnieuw naar bytes
            output = BytesIO()
            wb.save(output)
            output.seek(0)
            return output.read()  # return bytes

    def run(self):
        """Voer alle stappen uit en return Excel bestand als bytes."""
        self.prepare_data()
        return self.save_to_bytes()


# Voorbeeld van gebruik
#    scrumboard = {
#        "Backlog": [
#            {
#                "id": "B1",
#                "title": "Login functionaliteit",
#                "content": "Gebruiker kan inloggen met email en wachtwoord",
#                "priority": "Must Have",
#                "time_estimate": 5,
#                "assignee": "Jan",
#                "tags": ["auth", "frontend"],
#                "status": "Backlog",
#                "created_at": "2025-09-02",
#                "updated_at": "2025-09-02"
#            }
#        ],
#        "Sprints": [],
#        "In Progress": [],
#        "Review / Testing": [],
#        "Done": []
#    }
