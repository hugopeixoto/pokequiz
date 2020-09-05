import pokedex
import sys

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
    }[string_representation]

def operand(part):
    if part == "pokedex.national":
        return pokedex_national
    elif part == "pokedex.regional":
        return pokedex_regional
    elif part == "type":
        return pokemon_type
    elif part == "game.starter":
        return game_starter
    elif part == "evolution":
        return evolution_fn
    elif part == "not":
        return not_fn
    elif part.isdigit():
        return lambda species: [int(part)]
    elif part[0] == "'" and part[len(part) - 1] == "'":
        return lambda species: [part[1:len(part)-1]]

def build_query(query):
    parts = query.split(" ")

    if len(parts) == 1:
        op1 = operand(parts[0])
        query = op1
    if len(parts) == 3:
        op1 = operand(parts[0])
        opr = operations(parts[1])
        op2 = operand(parts[2])
        query = opr(op1, op2)
    elif len(parts) == 7:
        op1 = operand(parts[0])
        opr1 = operations(parts[1])
        op2 = operand(parts[2])
        opr2 = operations(parts[3])
        op3 = operand(parts[4])
        opr3 = operations(parts[5])
        op4 = operand(parts[6])

        q1 = opr1(op1, op2)
        q2 = opr3(op3, op4)
        query = opr2(q1, q2)

    return lambda species: any(query(species))

def find_pokemon(query):
    session = get_session([])

    query = build_query(query)

    pokemon = session.query(pokedex.db.tables.Pokemon).all()
    pokemon = [p for p in pokemon if query(p)]
    return pokemon

for p in find_pokemon(sys.argv[1]):
    print(p.identifier)
