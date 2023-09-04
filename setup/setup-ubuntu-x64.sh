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

if [ ! -f "$(which python3.10)" ]
then
  ${SUDO} add-apt-repository ppa:deadsnakes/ppa -y
  # torchvision does not support 3.11 yet
  ${SUDO} apt install python3.10 python3.10-dev python3.10-venv -y
fi

set -ex

${SUDO} apt-get -y install git-lfs lrzsz zip
git config --global credential.helper store

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
git clone https://github.com/hearmeneigh/dataset-rising.git

# dependencies
cd ${BASE_PATH}/tools/dataset-rising
python3.10 -m venv venv
source ./venv/bin/activate
pip install -v -r requirements.txt

# xformers
# pip install ninja
# pip install -v -U git+https://github.com/facebookresearch/xformers.git@main#egg=xformers

echo "Running AWS CLI configuration..."
aws configure

echo "Running Huggingface CLI configuration..."
huggingface-cli login

echo "Running Huggingface Accelerate configuration..."
accelerate config
