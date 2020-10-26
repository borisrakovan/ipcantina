import json

from flask import current_app


DELIMITER = '#'


def load_settings(raw_instructions=False):
    path = current_app.config['APP_SETTINGS_PATH']
    with open(path, 'r', encoding='utf-8') as f:
        settings = json.load(f)

        instructions = list(settings["instructions"].values())

        if raw_instructions:
            settings["instructions"] = (DELIMITER + "\n").join(instructions)
        else:
            settings["instructions"] = instructions

        return settings


def save_settings(settings):
    path = current_app.config['APP_SETTINGS_PATH']

    instructions = settings["instructions"].strip().split(DELIMITER)
    instructions = filter(lambda x: x != '', map(lambda x: x.strip(), instructions))

    instructions_json = {}
    for i, instruction in enumerate(instructions):
        instructions_json[str(i)] = instruction

    settings["instructions"] = instructions_json
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)

