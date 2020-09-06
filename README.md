# Experiments with veekun/pokedex, mostly

## Example queries

```
$ python potato.py "pokedex.regional == 1" | column -c 80
bulbasaur       chikorita       drifloon        rowlet
diglett         treecko         snivy           pikipek
diglett-alola   turtwig         chespin

$ python potato.py "type == 'dragon' and pokedex.national <= 151" | column -c 80
charizard-mega-x        dratini                 dragonite
exeggutor-alola         dragonair

$ python potato.py "evolution of evolution of game.starter"  | column -c 80
venusaur                sceptile                emboar
venusaur-mega           sceptile-mega           samurott
charizard               blaziken                chesnaught
charizard-mega-x        blaziken-mega           delphox
charizard-mega-y        swampert                greninja
blastoise               swampert-mega           greninja-battle-bond
blastoise-mega          torterra                greninja-ash
meganium                infernape               decidueye
typhlosion              empoleon                incineroar
feraligatr              serperior               primarina

$ python potato.py "pokemon.mega and pokedex.national <= 151" | column -c 80
venusaur-mega           pidgeot-mega            pinsir-mega
charizard-mega-x        alakazam-mega           gyarados-mega
charizard-mega-y        slowbro-mega            aerodactyl-mega
blastoise-mega          gengar-mega             mewtwo-mega-x
beedrill-mega           kangaskhan-mega         mewtwo-mega-y
```
