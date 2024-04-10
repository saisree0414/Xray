import requests

# Artifactory Configuration
artifactory_url = 'http://your-artifactory-url'
artifactory_username = 'admin'
artifactory_password = 'your_artifactory_password'

# Artifactory API endpoint for repository list
api_url = f'{artifactory_url}/artifactory/api/repositories'

# Artifactory API endpoint for Xray configuration
xray_api_url = f'{artifactory_url}/artifactory/api/xray'

# Authenticate with Artifactory
auth = (artifactory_username, artifactory_password)

# Get list of repositories from Artifactory
response = requests.get(api_url, auth=auth)

# Check if the request was successful
if response.status_code == 200:
    repositories = response.json()
    repos_without_xray = []

    # Iterate over repositories
    for repo in repositories:
        repo_name = repo['key']
        
        # Check Xray configuration for the repository
        xray_response = requests.get(f'{xray_api_url}/{repo_name}', auth=auth)
        
        if xray_response.status_code == 200:
            xray_config = xray_response.json()
            xray_enabled = xray_config.get('enabled', False)
            if not xray_enabled:
                repos_without_xray.append(repo_name)
        else:
            print(f"Failed to get Xray configuration for repository {repo_name}: {xray_response.text}")

    # Write repositories without Xray enabled to a file
    with open('repos_without_xray.txt', 'w') as f:
        f.write('\n'.join(repos_without_xray))
    print('List of repositories without Xray enabled has been written to repos_without_xray.txt')
else:
    print(f'Failed to fetch repositories from Artifactory: {response.text}')
