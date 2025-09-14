import aiohttp
import asyncio
import os
import requests


EXTENSION = '.gif'
group_size = 30
base_url = 'https://dka-hero.me/hm'
base_file = 'hori_'
headers = {
    'Referer': base_url,
    'User-Agent': 'Mozilla/5.0',
}
image_links = []
output_dir = 'out/'


def gen_url(ch_no):
    i = 1
    searching_group = True
    while searching_group:
        if ch_no >= (group_size * (i - 1) + 1) and \
            ch_no <= group_size * i:
            searching_group = False
        else:
            i += 1

    group_start = group_size * (i - 1) + 1
    group_end = group_size * i
    # return url like:
    # https://dka-hero.me/hm001_030/002/hori_
    return f'{base_url}{group_start:03d}_{group_end:03d}/{ch_no:03d}/{base_file}'


def url_exists(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False


def gather_links(url):
    i = 1
    evaulating = True
    while evaulating:
        final_url = f'{url}{i:03d}{EXTENSION}'
        if url_exists(final_url):
            print(f'{final_url}: Success')
            image_links.append(final_url)
            i += 1
        else:
            print(f'{final_url}: Failure')
            if image_links:
                evaulating = False
            else:
                i += 1


async def download_async(session, url):
    filename = url.split('/')[-1]
    print(f'Downloading: {filename}')
    try:
        async with session.get(url, headers=headers) as response:
            # Check for error
            if response.status != 200:
                print(f'HTTP error for {filename}: {response.status}')
                return

            # Write all at once cuz they very small (<100kb)
            os.makedirs(output_dir, exist_ok=True)
            data = await response.read()
            with open(f'{output_dir}{filename}', 'wb') as file:
                file.write(data)

        print(f'Saved: {url}')

    except aiohttp.ClientError as error:
        print(f'Request error for {url}: {error}')


async def download_files():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in image_links:
            tasks.append(download_async(session, url))
        await asyncio.gather(*tasks)


ch_no = 100
output_dir += f'{ch_no:02d}/'
gather_links(gen_url(ch_no))
asyncio.run(download_files())
