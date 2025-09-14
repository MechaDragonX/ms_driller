import aiohttp
import asyncio
import os
import requests


EXTENSION = '.gif'
base_url = 'https://dka-hero.me/hm001_030/001/hori_'
headers = {
    'Referer': base_url,
    'User-Agent': 'Mozilla/5.0',
}
image_links = []
output_dir = 'out/01/'


def url_exists(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False


def gather_links():
    i = 1
    evaulating = True
    while evaulating:
        url = f'{base_url}{i:03d}{EXTENSION}'
        if url_exists(url):
            print(f'{url}: Success')
            image_links.append(url)
            i += 1
        else:
            print(f'{url}: Failure')
            evaulating = False


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


gather_links()
asyncio.run(download_files())
