from google.cloud import secretmanager

def get_secret(secret_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/moviesbox-391505/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

# data_base = get_secret("DATABASE_URL")
# api_key = get_secret("API_KEY")
# secret_key = get_secret('SECRET_KEY')

# print('database', data_base)
# print('api key', api_key)
# print('secret key', secret_key)