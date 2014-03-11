#!/bin/bash

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

rsync \
    --archive \
    ${DIR}/ \
    -e 'ssh' \
    --rsync-path='sudo -u batman rsync' \
    root@nyx.kurz.pw:/var/customers/webs/batman/FlaskApp/ \
    --progress \
    -c \
    --exclude '*.dtbo' \
    --exclude '*.pyc' \
    --exclude '*.pyo' \
    --exclude '*.pyd' \
    --exclude '.git' \
    --exclude '.gitignore' \
    --exclude 'sync.sh' \
    --exclude 'venv' \
    --exclude 'config.py.example' \
    --delete
#    --exclude 'config.py' \

ssh root@nyx.kurz.pw sudo -u batman touch /var/customers/webs/batman/FlaskApp/flaskapp.wsgi
