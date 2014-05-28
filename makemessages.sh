#!/bin/bash
cd ~/workspace/fiee-dorsale/
for DIR in dorsale siteprofile
do
  cd $DIR
  echo $DIR
  python ../manage.py makemessages -a -e html,py,tex,txt
  python ../manage.py makemessages -a -d djangojs
  open locale/de/LC_MESSAGES/*.po
  cd ..
done
