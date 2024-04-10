import requests

# Set your Artifactory credentials and base URL
ARTIFACTORY_URL = "https://your-artifactory-url"
USERNAME = "your-username"
PASSWORD = "your-password"

# API endpoint for retrieving repositories
REPOSITORIES_ENDPOINT = f"{ARTIFACTORY_URL}/api/repositories"

# Function to retrieve repositories and their Xray index status
def get_repositories_xray_index_status():
    repositories_with_xray_index = []

    # Make request to Artifactory API
    response = requests.get(REPOSITORIES_ENDPOINT, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        repositories_data = response.json()
        
        for repo in repositories_data:
            repo_name = repo["key"]
            xray_index_enabled = repo.get("xrayIndex", False)  # Default value is False if property not present
            repositories_with_xray_index.append((repo_name, xray_index_enabled))
    
    return repositories_with_xray_index

# Function to write repository names into a file
def write_to_file(repositories_list):
    with open("repositories_without_xray_index.txt", "w") as file:
        for repo_name, xray_index_enabled in repositories_list:
            if not xray_index_enabled:
                file.write(repo_name + "\n")

if __name__ == "__main__":
    repositories_xray_index_status = get_repositories_xray_index_status()
    write_to_file(repositories_xray_index_status)
