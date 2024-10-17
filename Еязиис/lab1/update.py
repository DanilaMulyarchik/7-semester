import os
import requests
from bs4 import BeautifulSoup
#python -m http.server 7000
#ngrok http 7000


def get_file_urls(root_url, base_url=""):
    file_urls = []
    try:
        response = requests.get(root_url + base_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a'):
                href = link.get('href')
                if href and href != "../":
                    if href[-1] == '/':
                        subdirectory_url = base_url + '/' + href
                        file_urls += get_file_urls(root_url, subdirectory_url)
                    else:
                        file_urls.append(root_url + base_url + '/' + href)
        else:
            print(f"Error {root_url + base_url} \n {response.status_code}")
    except Exception as e:
        print(f"Error {str(e)}")
    return file_urls


def download_file(url, save_path):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        else:
            print(f"Error{url} \n {response.status_code}")
    except Exception as e:
        print(f"Error {url}: {str(e)}")


def update():
    root_url = "http://localhost:7000"

    save_directory = "downloaded_files"

    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    file_urls = get_file_urls(root_url)

    with open('paths.txt', 'r') as f:
        all_file_name = [i[:-1] if i[-1] == '\n' else i for i in f.readlines()]

    for url in file_urls:
        relative_path = url.replace(root_url, "")
        save_path = save_directory + relative_path

        if save_path not in all_file_name:
            with open('paths.txt', 'a') as f:
                f.write(save_path + '\n')

        save_dir = os.path.dirname(save_path)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        download_file(url, save_path)




