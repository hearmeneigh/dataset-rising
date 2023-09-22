import subprocess
import os

def main():
    username = os.environ.get('DB_USERNAME', 'root')
    password = os.environ.get('DB_PASSWORD', 'root')
    port = int(os.environ.get('DB_PORT', '27017'))

    cmd = f'docker start dataset-rising-mongo || docker run --name dataset-rising-mongo --restart always -e "MONGO_INITDB_ROOT_USERNAME={username}" -e "MONGO_INITDB_ROOT_PASSWORD={password}" -p "{port}:{port}" -d mongo:6'
    print(f"Running '{cmd}'...".replace(password, '******'))

    subprocess.run(
        cmd,
        shell=True, cwd=os.path.dirname(__file__), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )

    print('✅ Done!')


if __name__ == "__main__":
    main()
