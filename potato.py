import pokedex
import sys
import re

import pokedex.cli.search
import pokedex.db
import pokedex.db.load
import pokedex.db.util
import pokedex.lookup

from pokedex import defaults

def get_session(args):
    engine_uri, got_from = defaults.get_default_db_uri_with_origin()
    return pokedex.db.connect(engine_uri)

def get_lookup(args, session=None, recreate=False):
    index_dir, got_from = defaults.get_default_index_dir_with_origin()
    lookup = pokedex.lookup.PokedexLookup(index_dir, session=session)

    return lookup

def pokedex_regional(pokemon_instance):
    return [
        d.pokedex_number
        for d in pokemon_instance.species.dex_numbers
        if d.pokedex.is_main_series == 1 and d.pokedex_id != 1
    ]

def pokedex_national(pokemon_instance):
    return [
        d.pokedex_number
        for d in pokemon_instance.species.dex_numbers
        if d.pokedex.is_main_series == 1 and d.pokedex_id == 1
    ]

def pokemon_type(pokemon_instance):
    return [
        d.identifier
        for d in pokemon_instance.types
    ]

def pokemon_mega(pokemon_instance):
    if pokemon_instance.default_form.is_mega:
        return [pokemon_instance]
    else:
        return []

def pokemon_default_form(pokemon_instance):
    if pokemon_instance.default_form.form_identifier == None:
        return [pokemon_instance]
    else:
        return []


def game_starter(pokemon_instance):
    return [
        True
        for d in pokemon_instance.species.dex_numbers
        if d.pokedex.is_main_series == 1
            and d.pokedex_id not in [1, 13,14, 18,19,20, 22,23,24,25]
            and d.pokedex_number <= 9
            and (d.pokedex_number - 1) % 3 == 0
    ]

def not_fn(fn):
    return lambda species: [not any(fn(species))]

def evolution_fn(fn):
    def f(pokemon_instance):
        if pokemon_instance.species.parent_species is None:
            return []
        else:
            return [any(fn(p)) for p in pokemon_instance.species.parent_species.pokemon]

    return f


def operations(string_representation):
    binop = lambda op: lambda x, y: lambda species: [any(op(a, b) for a in x(species) for b in y(species))]
    return {
        ">=": binop(lambda a, b: a >= b),
        "<=": binop(lambda a, b: a <= b),
        "==": binop(lambda a, b: a == b),
        "and": binop(lambda a, b: a and b),
        "or": binop(lambda a, b: a or b),
        "of": lambda x, y: x(y),
    }[string_representation[1]]

def operand(part):
    t, token = part

    if t == "identifier":
        return {
            "pokedex.national": pokedex_national,
            "pokedex.regional": pokedex_regional,
            "type": pokemon_type,
            "pokemon.mega": pokemon_mega,
            "pokemon.default_form": pokemon_default_form,
            "game.starter": game_starter,
            "evolution": evolution_fn,
            "not": not_fn,
        }[token]
    else:
        return lambda species: [token]

def build_query(query):
    scanner = re.Scanner([
        (r"==|<=|>=|and|or|of", lambda s,t: ("operator", t)),
        (r"[a-z._]+", lambda s,t: ("identifier", t)),
        (r"[0-9]+", lambda s,t: ("number", int(t))),
        (r"'.*'", lambda s,t: ("string", t[1:len(part)-1])),
        (r"\s+", None),
    ])

    parts, _ = scanner.scan(query)

    if len(parts) == 1:
        op1 = operand(parts[0])
        query = op1
    if len(parts) == 3:
        op1 = operand(parts[0])
        opr = operations(parts[1])
        op2 = operand(parts[2])
        query = opr(op1, op2)
    if len(parts) == 5:
        op1 = operand(parts[0])
        opr1 = operations(parts[1])
        op2 = operand(parts[2])
        opr2 = operations(parts[3])
        op3 = operand(parts[4])
        query = opr1(op1, opr2(op2, op3))
    elif len(parts) == 7:
        op1 = operand(parts[0])
        opr1 = operations(parts[1])
        op2 = operand(parts[2])
        opr2 = operations(parts[3])
        op3 = operand(parts[4])
        opr3 = operations(parts[5])
        op4 = operand(parts[6])
        query = opr2(opr1(op1, op2), opr3(op3, op4))
    elif len(parts) == 9:
        op1 = operand(parts[0])
        opr1 = operations(parts[1])
        op2 = operand(parts[2])
        opr2 = operations(parts[3])
        op3 = operand(parts[4])
        opr3 = operations(parts[5])
        op4 = operand(parts[6])
        opr4 = operations(parts[7])
        op5 = operand(parts[8])
        query = opr3(opr1(op1, opr2(op2, op3)), opr4(op4, op5))

    return lambda species: any(query(species))

def find_pokemon(query):
    session = get_session([])

    query = build_query(query)

    pokemon = session.query(pokedex.db.tables.Pokemon).all()
    pokemon = [p for p in pokemon if query(p)]
    return pokemon

for p in find_pokemon(sys.argv[1]):
    print(p.identifier)
