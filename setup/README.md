# OS Setup Scripts

> Convenience installer scripts that install Dataset Rising on top of a vanilla OS installation
>
> You will only need to do run this script if you are setting up a new machine for training,
> for example a new EC2, Google Cloud, Vast AI, RunPod, etc. instance. 
>
> **You do not need to run these scripts on your local machine.**

## Ubuntu
* Assumes CUDA is already installed
  * CUDA is typically provided by the cloud provider
* Installs Python 3.11
* Installs Docker 24.x
* Installs AWS CLI
* Installs Dataset Rising
* Sets up a workspace directory in `/${BASE_PATH}`
  * `BASE_PATH` defaults to `/workspace`

### Usage

```bash
./setup-ubuntu-x64.sh
```
