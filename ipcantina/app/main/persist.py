import json

from flask import current_app

DELIMITER = '#'


def load_instructions(raw=False):
    path = current_app.config['INSTRUCTIONS_TEXT_PATH']
    with open(path, 'r', encoding='utf-8') as f:
        jsn = json.load(f)

        instructions = list(jsn.values())
        if raw:
            return (DELIMITER + "\n").join(instructions)

        return instructions


def save_instructions(text):
    instructions = text.strip().split(DELIMITER)
    instructions = filter(lambda x: x != '', map(lambda x: x.strip(), instructions))

    jsn = {}
    for i, instruction in enumerate(instructions):
        jsn[str(i)] = instruction

    path = current_app.config['INSTRUCTIONS_TEXT_PATH']
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(jsn, f, indent=4, ensure_ascii=False)


def save_prices(a, b, c):
    path = current_app.config['DEFAULT_PRICES_PATH']
    prices = {'A': a, 'B': b, 'C': c}
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(prices, f, indent=4)

def load_prices():
    with open(current_app.config['DEFAULT_PRICES_PATH'], 'r', encoding='utf-8') as f:
        return json.load(f)
