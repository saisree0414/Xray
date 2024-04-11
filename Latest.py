import requests
import csv

def get_repo_list(base_url, username, password):
    auth = (username, password)
    url = f"{base_url}/artifactory/api/repositories"
    response = requests.get(url, auth=auth)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve repository list. Status code: {response.status_code}")
        return None

def get_xray_index(base_url, username, password, repo_key):
    auth = (username, password)
    url = f"{base_url}/artifactory/api/xrayIndex/{repo_key}"
    response = requests.get(url, auth=auth)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve Xray index for {repo_key}. Status code: {response.status_code}")
        return None

def write_to_csv(repo_list, csv_file, base_url, username, password):
    with open(csv_file, mode='w', newline='') as file:
        fieldnames = ['repository_name', 'xray_index_key', 'xray_index_value']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for repo in repo_list:
            if repo['type'] in ['remote', 'federated']:
                repo_name = repo['key']
                xray_index = get_xray_index(base_url, username, password, repo_name)
                if xray_index:
                    for key, value in xray_index.items():
                        writer.writerow({'repository_name': repo_name, 'xray_index_key': key, 'xray_index_value': value})

def main():
    base_url = 'YOUR_ARTIFACTORY_BASE_URL'
    username = 'YOUR_USERNAME'
    password = 'YOUR_PASSWORD'
    csv_file = 'repo_xray_index.csv'

    repo_list = get_repo_list(base_url, username, password)
    if repo_list:
        write_to_csv(repo_list, csv_file, base_url, username, password)
        print(f"Repository Xray index data written to {csv_file}")

if __name__ == "__main__":
    main()
