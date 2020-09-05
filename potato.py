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


def poop(query):
    session = get_session([])

    pokemon = session.query(pokedex.db.tables.Pokemon).all()

    if query == "pokedex.national <= 151":
        pokemon = [
            p for p in pokemon
            if any(d for d in p.species.dex_numbers if d.pokedex_id == 1 and d.pokedex_number <= 151)
        ]

    if query == "pokedex.regional == 1":
        pokemon = [
            p for p in pokemon
            if any(d for d in p.species.dex_numbers if d.pokedex.is_main_series == 1 and d.pokedex_id != 1 and d.pokedex_number == 1)
        ]

    return pokemon

for p in poop(sys.argv[1]):
    print(p.identifier)
