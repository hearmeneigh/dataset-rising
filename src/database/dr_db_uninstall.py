import subprocess
import os


def main():
    print('Running \'docker stop dataset-rising-mongo\'...')
    subprocess.run('docker stop dataset-rising-mongo || echo "no instance to stop"', shell=True, cwd=os.path.dirname(__file__), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print('Running \'docker rm dataset-rising-mongo\'...')
    subprocess.run('docker rm dataset-rising-mongo', shell=True, cwd=os.path.dirname(__file__), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print('✅ Done!')


if __name__ == "__main__":
    main()

