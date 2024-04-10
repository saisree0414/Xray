#!/bin/bash

# Output file name
output_file="repositories_with_xrayIndex_false.txt"

# Fetch remote repositories
remote_repositories=$(jfrog rt repos --type=remote)

# Fetch federated repositories
federated_repositories=$(jfrog rt repos --type=federated)

# Function to check if xrayIndex is false and write to output file
check_and_write() {
    repository_name=$1
    xray_index_value=$2

    if [ "$xray_index_value" = "false" ]; then
        echo "$repository_name" >> "$output_file"
    fi
}

# Loop through remote repositories
while IFS= read -r repo; do
    repo_config=$(jfrog rt config show "$repo")
    xray_index=$(echo "$repo_config" | jq -r '.xrayIndex')
    check_and_write "$repo" "$xray_index"
done <<< "$remote_repositories"

# Loop through federated repositories
while IFS= read -r repo; do
    repo_config=$(jfrog rt config show "$repo")
    xray_index=$(echo "$repo_config" | jq -r '.xrayIndex')
    check_and_write "$repo" "$xray_index"
done <<< "$federated_repositories"

echo "List of repositories with xrayIndex set to false written to $output_file"
