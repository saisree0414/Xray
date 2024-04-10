import requests

# Set your Artifactory credentials and base URL
username = 'your_username'
password = 'your_password'
base_url = 'https://your_artifactory_instance_url/artifactory/api'

# Get a list of repositories
def get_repositories():
    url = f'{base_url}/repositories'
    response = requests.get(url, auth=(username, password))
    repositories = response.json()
    return repositories

# Filter federated, remote repositories not enabled for indexing
def filter_repositories(repositories):
    filtered_repositories = []
    for repo in repositories:
        if repo['type'] == 'remote' and repo['packageType'] != 'local' and not repo['enableIndexing']:
            filtered_repositories.append(repo['key'])
    return filtered_repositories

# Main function to get the list of repositories
def main():
    repositories = get_repositories()
    filtered_repositories = filter_repositories(repositories)
    print("Federated, remote repositories not enabled for indexing:")
    for repo in filtered_repositories:
        print(repo)

if __name__ == "__main__":
    main()
