import asyncio

from glob import glob
import httpx
from dill import dump

async def main():
    mons = {}
    for form in ['regular', 'shiny', 'cday']:
        mons[form] = []
        for mon in glob(f'{form}/*.gif'):
            mon_split = mon.split('\\')
            mons[form].append(mon_split[1].lower().replace('.gif', ''))

    for rarity in ['common', 'uncommon', 'rare', 'legendary']:
        mons[rarity] = []

    for mon in mons['regular']:
        print(mon)
        async with httpx.AsyncClient() as client:
            resp = await client.get(f'https://pokeapi.co/api/v2/pokemon-species/{mon}')
        mon_json = resp.json()
        async with httpx.AsyncClient() as client:
            resp = await client.get(mon_json['evolution_chain']['url'])
        chain_json = resp.json()
        if mon_json['is_legendary'] or mon_json['is_mythical']:
            mons['legendary'].append(mon)
        elif not mon_json['evolves_from_species'] is None:
            if len(chain_json['chain']['evolves_to']) == 0:
                mons['rare'].append(mon)
            else:
                mons['uncommon'].append(mon)
        else:
            if len(chain_json['chain']['evolves_to']) == 0:
                mons['uncommon'].append(mon)
            else:
                mons['common'].append(mon)
    with open('mons.dill', 'wb') as f:
        dump(mons, f)


loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait([main()]))
loop.close()
