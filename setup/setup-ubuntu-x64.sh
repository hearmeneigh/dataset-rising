#!/bin/bash

if [ -z "${BASE_PATH}" ]
then
  BASE_PATH='/workspace'
fi

if [ "$(whoami)" != 'root' ]
then
  SUDO='sudo'
else
  SUDO=''
fi

# Install Python 3.11
if [ ! -f "$(which python3.11)" ]
then
  ${SUDO} add-apt-repository ppa:deadsnakes/ppa -y
  ${SUDO} apt install python3.11 python3.11-dev python3.11-venv -y
fi

set -ex

# Install tools
${SUDO} apt-get -y install git-lfs lrzsz zip docker.io
git config --global credential.helper store

if [ "$(whoami)" != 'root' ]
then
  ${SUDO} usermod -aG docker "$(whoami)"
  ${SUDO} su - "$(whoami)"
fi

# Install AWS CLI
mkdir /tmp/aws
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "/tmp/aws/awscliv2.zip"
cd /tmp/aws
unzip awscliv2.zip
${SUDO} /tmp/aws/aws/install


${SUDO} mkdir -p "${BASE_PATH}"

if [ "$(whoami)" != 'root' ]
then
  ${SUDO} chown "$(whoami):$(whoami)" "${BASE_PATH}"
fi

mkdir -p "${BASE_PATH}/cache/huggingface"
mkdir -p "${BASE_PATH}/output"
mkdir -p "${BASE_PATH}/checkpoints"
mkdir -p "${BASE_PATH}/downloads"
mkdir -p "${BASE_PATH}/tools"

cd "${BASE_PATH}/tools"
python3.11 -m pip install --upgrade DatasetRising

# xformers
# pip install ninja
# pip install -v -U git+https://github.com/facebookresearch/xformers.git@main#egg=xformers

echo "Running AWS CLI configuration..."
aws configure

echo "Running Huggingface CLI configuration..."
huggingface-cli login

echo "Running Huggingface Accelerate configuration..."
accelerate config
