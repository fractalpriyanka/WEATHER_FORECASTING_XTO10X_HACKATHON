import requests
import os

class GitHubStorage:
    def __init__(self, repo, token):
        self.repo = repo  
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }

    def download_file(self, artifact_name, local_path):
        url = f"https://api.github.com/repos/{self.repo}/actions/artifacts"
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            raise Exception(f"Failed to list artifacts: {response.status_code}")
        
        artifacts = response.json().get('artifacts', [])
        for artifact in sorted(artifacts, key=lambda x: x['created_at'], reverse=True):
            if artifact['name'] == artifact_name:
                download_url = artifact['archive_download_url']
                r = requests.get(download_url, headers=self.headers, stream=True)
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                with open(local_path + ".zip", 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                # Unzip the artifact (GitHub provides a zip)
                import zipfile
                with zipfile.ZipFile(local_path + ".zip", 'r') as zip_ref:
                    zip_ref.extractall(os.path.dirname(local_path))
                os.remove(local_path + ".zip")
                # Rename to expected path if needed
                extracted_files = os.listdir(os.path.dirname(local_path))
                for file in extracted_files:
                    if file.startswith("xgb_model") and artifact_name == "model":
                        os.rename(os.path.join(os.path.dirname(local_path), file), local_path)
                    elif file.endswith("preprocessed.csv") and artifact_name == "dataset":
                        os.rename(os.path.join(os.path.dirname(local_path), file), local_path)
                print(f"Downloaded {artifact_name} to {local_path}")
                return
        raise Exception(f"Artifact {artifact_name} not found")

if __name__ == "__main__":
    repo = "Bhawesh-Agrawal/weather-app"
    token = "YOUR_GITHUB_TOKEN"
    storage = GitHubStorage(repo, token)
    storage.download_file("dataset", "data/mandi_weather_data_preprocessed.csv")
    storage.download_file("model", "model/xgb_model_latest.pkl")