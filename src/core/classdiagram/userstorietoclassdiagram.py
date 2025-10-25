import json
import re

def userstories_to_classdiagram(userstories) -> str:
    print(userstories)
    classes = {}
    relations = set()

    for story in userstories:
        actor = story["user_story"]["as_a"].strip().capitalize()
        method_raw = story["user_story"]["i_want"].strip()

        # Genereer methodenaam -> lowercase, spaties naar underscores
        method = re.sub(r"\W+", "_", method_raw.lower()).strip("_") + "()"

        if actor not in classes:
            classes[actor] = {
                "id": actor,
                "name": actor,
                "attributes": [],
                "methods": []
            }

        if method not in classes[actor]["methods"]:
            classes[actor]["methods"].append(method)

        # Relaties: kijk in i_want of so_that of er andere actoren genoemd zijn
        for other_story in userstories:
            other_actor = other_story["user_story"]["as_a"].strip().capitalize()
            if other_actor != actor and (
                other_actor.lower() in story["user_story"]["i_want"].lower()
                or other_actor.lower() in story["user_story"]["so_that"].lower()
            ):
                relations.add(tuple(sorted([actor, other_actor])))

    output = {
        "classes": list(classes.values()),
        "relations": [{"from": a, "to": b, "type": "association"} for a, b in relations]
    }

    return json.dumps(output, indent=4, ensure_ascii=False)