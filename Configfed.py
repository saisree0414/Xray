import requests
import csv

def get_repo_configuration(base_url, username, password, repo_key):
    auth = (username, password)
    url = f"{base_url}/artifactory/api/repositories/{repo_key}"
    response = requests.get(url, auth=auth)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve repository configuration for {repo_key}. Status code: {response.status_code}")
        return None

def write_to_csv(repo_configurations, csv_file):
    with open(csv_file, mode='w', newline='') as file:
        fieldnames = ['name', 'type', 'url']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for repo_config in repo_configurations:
            writer.writerow(repo_config)

def main():
    base_url = 'YOUR_ARTIFACTORY_BASE_URL'
    username = 'YOUR_USERNAME'
    password = 'YOUR_PASSWORD'
    csv_file = 'repo_configurations.csv'

    # Fetching all repositories
    auth = (username, password)
    url = f"{base_url}/artifactory/api/repositories"
    response = requests.get(url, auth=auth)
    if response.status_code == 200:
        repositories = response.json()
        repo_configurations = []
        for repo in repositories:
            if repo['type'] in ['remote', 'federated']:
                repo_config = get_repo_configuration(base_url, username, password, repo['key'])
                if repo_config:
                    repo_configurations.append({
                        'name': repo_config['key'],
                        'type': repo_config['type'],
                        'url': repo_config['url']
                    })
        write_to_csv(repo_configurations, csv_file)
        print(f"All repository configurations written to {csv_file}")
    else:
        print(f"Failed to retrieve repository configurations. Status code: {response.status_code}")

if __name__ == "__main__":
    main()
