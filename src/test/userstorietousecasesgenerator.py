import re


def compile_userstories_to_usecase_json(userstories, system_name="Schoolportaal"):
    actors_map = {}  # name -> id
    usecases_map = {}  # name -> id
    relations = []
    use_cases = []
    actors = []

    actor_counter = 1
    usecase_counter = 1

    # Helper functie om use case name clean te maken
    def clean_name(name):
        return name.strip().capitalize()

    for us in userstories:
        # Actor ophalen
        actor_name = clean_name(us["user_story"]["as_a"])
        if actor_name not in actors_map:
            actor_id = f"A{actor_counter}"
            actors_map[actor_name] = actor_id
            actors.append({"id": actor_id, "name": actor_name})
            actor_counter += 1
        else:
            actor_id = actors_map[actor_name]

        # Use case ophalen
        usecase_name = clean_name(us["user_story"]["i_want"])
        if usecase_name not in usecases_map:
            usecase_id = f"UC{usecase_counter}"
            usecases_map[usecase_name] = usecase_id
            use_cases.append({"id": usecase_id, "name": usecase_name})
            usecase_counter += 1
        else:
            usecase_id = usecases_map[usecase_name]

        # Relatie actor -> use case
        relations.append({"actor_id": actor_id, "use_case_id": usecase_id})

        # Check so_that voor includes (kijk of er een usecase in de text genoemd wordt)
        so_that_text = us["user_story"].get("so_that", "").lower()
        for uc_name, uc_id in usecases_map.items():
            if uc_name.lower() in so_that_text and uc_id != usecase_id:
                # Voeg include toe aan huidige use case
                uc = next(u for u in use_cases if u["id"] == usecase_id)
                if "includes" not in uc:
                    uc["includes"] = []
                if uc_id not in uc["includes"]:
                    uc["includes"].append(uc_id)

    return {
        "system": system_name,
        "actors": actors,
        "use_cases": use_cases,
        "relations": relations
    }


# Voorbeeldgebruik:
userstories = [
    {
        "id": "US1",
        "title": "Inloggen student",
        "user_story": {
            "as_a": "student",
            "i_want": "inloggen",
            "so_that": "ik mijn cijfers kan bekijken"
        }
    },
    {
        "id": "US2",
        "title": "Cijfers bekijken student",
        "user_story": {
            "as_a": "student",
            "i_want": "cijfers bekijken",
            "so_that": "ik mijn voortgang kan volgen"
        }
    },
    {
        "id": "US3",
        "title": "Cijfers invoeren docent",
        "user_story": {
            "as_a": "docent",
            "i_want": "cijfers invoeren",
            "so_that": "studenten hun resultaten kunnen zien"
        }
    }
]

result_json = compile_userstories_to_usecase_json(userstories)
import json

print(json.dumps(result_json, indent=2))
