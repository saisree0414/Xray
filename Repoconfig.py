import requests
import csv

def get_repo_configuration(base_url, api_key, repo_key):
    headers = {
        'X-JFrog-Art-Api': api_key
    }
    url = f"{base_url}/artifactory/api/repositories/{repo_key}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve repository configuration for {repo_key}. Status code: {response.status_code}")
        return None

def write_to_csv(repo_config, csv_file):
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=repo_config.keys())
        writer.writeheader()
        writer.writerow(repo_config)

def main():
    base_url = 'YOUR_ARTIFACTORY_BASE_URL'
    api_key = 'YOUR_API_KEY'

    # Fetching all repositories
    headers = {
        'X-JFrog-Art-Api': api_key
    }
    url = f"{base_url}/artifactory/api/repositories"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        repositories = response.json()
        for repo in repositories:
            if repo['type'] in ['remote', 'federated']:
                repo_config = get_repo_configuration(base_url, api_key, repo['key'])
                if repo_config:
                    csv_file = f"{repo['key']}_config.csv"
                    write_to_csv(repo_config, csv_file)
                    print(f"Repository configuration written to {csv_file}")
    else:
        print(f"Failed to retrieve repository configurations. Status code: {response.status_code}")

if __name__ == "__main__":
    main()
