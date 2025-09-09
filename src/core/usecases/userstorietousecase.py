def userstories_to_usecase_json(input_json, system_name="Schoolportaal"):
    """
    Zet een lijst van user stories om naar de gewenste use case JSON structuur.

    Args:
        input_json (list): lijst van user stories in jouw format
        system_name (str): naam van het systeem

    Returns:
        dict: JSON-structuur met actors, use_cases en relations
    """
    actors_map = {}  # name -> id
    usecases_map = {}  # name -> id
    relations = []
    use_cases = []
    actors = []

    actor_counter = 1
    usecase_counter = 1

    def clean_name(name):
        return name.strip().capitalize()

    for us in input_json:
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

        # Check so_that voor includes (kijk of een bestaande use case genoemd wordt)
        so_that_text = us["user_story"].get("so_that", "").lower()
        for uc_name, uc_id in usecases_map.items():
            if uc_name.lower() in so_that_text and uc_id != usecase_id:
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