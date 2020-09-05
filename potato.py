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


def operations(string_representation):
    return {
        ">=": lambda x, y: [any(a >= b for a in x for b in y)],
        "<=": lambda x, y: [any(a <= b for a in x for b in y)],
        "==": lambda x, y: [any(a == b for a in x for b in y)],
        "and": lambda x, y: [any(a and b for a in x for b in y)],
    }[string_representation]

def operand(part):
    if part == "pokedex.national":
        return pokedex_national
    elif part == "pokedex.regional":
        return pokedex_regional
    elif part == "type":
        return pokemon_type
    elif part.isdigit():
        return lambda species: [int(part)]
    elif part[0] == "'" and part[len(part) - 1] == "'":
        return lambda species: [part[1:len(part)-1]]

def build_query(query):
    parts = query.split(" ")

    if len(parts) == 3:
        op1 = operand(parts[0])
        opr = operations(parts[1])
        op2 = operand(parts[2])
        query = lambda species: opr(op1(species), op2(species))
    elif len(parts) == 7:
        op1 = operand(parts[0])
        opr1 = operations(parts[1])
        op2 = operand(parts[2])
        opr2 = operations(parts[3])
        op3 = operand(parts[4])
        opr3 = operations(parts[5])
        op4 = operand(parts[6])

        q1 = lambda species: opr1(op1(species), op2(species))
        q2 = lambda species: opr3(op3(species), op4(species))
        query = lambda species: opr2(q1(species), q2(species))

    return lambda species: any(query(species))

def poop(query):
    session = get_session([])

    query = build_query(query)

    pokemon = session.query(pokedex.db.tables.Pokemon).all()
    pokemon = [p for p in pokemon if query(p)]
    return pokemon

for p in poop(sys.argv[1]):
    print(p.identifier)
