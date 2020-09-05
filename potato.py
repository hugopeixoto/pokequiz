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

def operations(string_representation):
    return {
        ">=": lambda x, y: any(a >= b for a in x for b in y),
        "<=": lambda x, y: any(a <= b for a in x for b in y),
        "==": lambda x, y: any(a == b for a in x for b in y),
    }[string_representation]

def operand(part):
    if part == "pokedex.national":
        return pokedex_national
    elif part == "pokedex.regional":
        return pokedex_regional
    elif part.isdigit():
        return lambda species: [int(part)]
    else:
        raise "oops"

def poop(query):
    session = get_session([])

    pokemon = session.query(pokedex.db.tables.Pokemon).all()

    parts = query.split(" ")

    op1 = operand(parts[0])
    opr = operations(parts[1])
    op2 = operand(parts[2])
    query = lambda species: opr(op1(species), op2(species))

    pokemon = [p for p in pokemon if query(p)]
    return pokemon

for p in poop(sys.argv[1]):
    print(p.identifier)
