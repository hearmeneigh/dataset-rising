# OS Setup Scripts

> Installer scripts that install Dataset Rising on top of a new vanilla OS installation

Typically, you will only need to do this if you are setting up a new machine for training,
for example a new EC2, Google Cloud, Vast AI, RunPod, etc. instance. 

You do not need to run these scripts on your local machine.

## Ubuntu
* Assumes CUDA is already installed
* Installs Python 3.10
* Installs AWS CLI
* Installs Dataset Rising to `/workspace/tools/dataset-rising`

### Usage

```bash
./setup-ubuntu-x64.sh
```
