#!/bin/bash

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

ssh root@10.8.0.3 mount -o remount,rw /

rsync \
    --archive \
    ${DIR}/ \
    -e ssh \
    root@10.8.0.3:/home/root/lichtschranke/ \
    --progress \
    --exclude '*.dtbo' \
    --exclude '*.pyc' \
    --exclude '*.pyo' \
    --exclude '*.pyd' \
    --exclude '.git' \
    --delete

ssh root@10.8.0.3 mount -o remount,ro /
