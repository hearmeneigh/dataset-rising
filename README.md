## Requirements
* Python3
* Docker


## Setting Up
Creates a virtual environment, installs packages, and sets up a MongoDB database on Docker. 

```bash
./up.sh
```

## Shutting Down
Stops the MongoDB database container. The database can be restarted by running `./up.sh` again.

```bash
./down.sh
```


## Uninstall
Warning: This step **removes** the MongoDB database container and all data stored on it.

```bash
./uninstall.sh
```
