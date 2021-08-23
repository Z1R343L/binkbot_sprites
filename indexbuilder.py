import asyncio
from os.path import exists

from glob import glob
import httpx
from dill import dump, load

async def main():
    mons = {}
    for form in ['regular', 'shiny', 'cday']:
        mons[form] = []
        for mon in glob(f'{form}/*.gif'):
            mon_split = mon.split('\\')
            mons[form].append(mon_split[1].lower().replace('.gif', ''))

    for rarity in ['common', 'uncommon', 'rare', 'legendary']:
        mons[rarity] = []

    if not exists('cache.dill'):
        cache = {}
        cache['species'] = {}
        cache['chain'] = {}
        for mon in mons['regular']:
            print(mon)
            async with httpx.AsyncClient() as client:
                resp = await client.get(f'https://pokeapi.co/api/v2/pokemon-species/{mon}')
            mon_json = resp.json()
            async with httpx.AsyncClient() as client:
                resp = await client.get(mon_json['evolution_chain']['url'])
            chain_json = resp.json()
            cache['species'][mon] = mon_json
            cache['chain'][mon] = chain_json
            with open('cache.dill', 'wb') as f:
                dump(cache, f)
    else:
        print("cahe found!")


    with open('cache.dill', 'rb') as f:
        cache = load(f)
    for mon in mons['regular']:
        print(mon)
        if cache['species'][mon]['is_legendary'] or cache['species'][mon]['is_mythical']:
            mons['legendary'].append(mon)
        elif cache['species'][mon]['evolves_from_species'] is not None:
            print(len(cache['chain'][mon]['chain']['evolves_to']))
            print(str(cache['chain'][mon]))
            if cache['chain'][mon]['chain']['evolves_to'][len(cache['chain'][mon]['chain']['evolves_to'])]:
                mons['rare'].append(mon)
            else:
                mons['uncommon'].append(mon)
        else:
            if len(cache['chain'][mon]['chain']['evolves_to']) == 0:
                mons['uncommon'].append(mon)
            else:
                mons['common'].append(mon)
    with open('mons.dill', 'wb') as f:
        dump(mons, f)


loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait([main()]))
loop.close()
