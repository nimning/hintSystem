### Production
```
/etc/init.d/hint-sockjs-4350 {start|restart|stop}
/etc/init.d/hint-rest-7250 {start|restart|stop}
/etc/init.d/hint-rest-7251 {start|restart|stop}
/etc/init.d/hint-rest-7252 {start|restart|stop}
/etc/init.d/hint-rest-7253 {start|restart|stop}
/etc/init.d/hint-rest-7254 {start|restart|stop}
```

### Test servers
```
python rest_server/rest_server.py --port=1234
python sockjs_server/sockjs_server.py --port=4321 --rest_port=1234
```

