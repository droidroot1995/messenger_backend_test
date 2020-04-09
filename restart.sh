#!/bin/zsh

systemctl restart nginx
systemctl restart redis-server
systemctl restart celery
systemctl restart celery-flower
systemctl restart celery-beat
systemctl restart peerjs
systemctl restart gunicorn.socket
systemctl restart gunicorn
