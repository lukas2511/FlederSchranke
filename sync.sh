#!/bin/bash

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

ssh -o ProxyCommand="ssh colo1.kurz.pw nc %h %p 2> /dev/null" root@10.8.0.3 mount -o remount,rw /

rsync \
    --archive \
    ${DIR}/ \
    -e 'ssh -o ProxyCommand="ssh colo1.kurz.pw nc %h %p 2> /dev/null"' \
    root@10.8.0.3:/home/root/lichtschranke/ \
    --progress \
    --exclude '*.dtbo' \
    --exclude '*.pyc' \
    --exclude '*.pyo' \
    --exclude '*.pyd' \
    --exclude '.git' \
    --exclude 'sync.sh' \
    --exclude 'flaskapp' \
    --delete

ssh -o ProxyCommand="ssh colo1.kurz.pw nc %h %p 2> /dev/null" root@10.8.0.3 mount -o remount,ro /
