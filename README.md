# VyControl
[VyOS](https://www.vyos.io/) frontend made in Python / Django using VyOS new 1.3 API server

<p align="center">
<img align="center" width="150" height="150" src="https://storage.googleapis.com/vycontrol/logos/logo_transparent.png">
</p>




It will work with a single VyoS server or to multiple VyOS servers, so datacenters which do not want share same firewall to different customers will not need to install several VyControl to each customer. That's why the name VyControl.

## community
* Slack Channel https://vyos.slack.com/archives/C012X7DGASY
* Forum Post https://forum.vyos.io/t/vycenter-alpha-stage-announcement-vyos-web-interface/5221/4

## features
# in alpha stage we're going to provide just essential device config, interfaces and firewall, as proof of concencept, as well config module basic cruds (users, groups and vyOS Servers)
# basic authentication - use django admin to create superuser than http://127.0.0.1:8000/admin/login/?next=/admin/ to create a new user, after that you can use VyControl


### interfaces module
* list interfaces - alpha
* show interface - alpha
* unset/set firewall interface - todo
* change interface parameters - todo

### firewall module
* basic firewall rules creation proof of concept - done
* basic list firewall rules - done
* basic add firewall rules - done
* basic edit firewall rules - done
* basic firewall create - done
* change firewall rules order - todo
* delete firewall rules - todo

## other modules - todo
* ospf
* bgp
* ipsec
* openvpn
* reports (maybe collecting using snmp)
* ssh management 
* system login managament
* nat
* dhcp servers
* static routes

### config module
* VyControl users crud - todo
* vyos instance using database - done
* full vyos instances crud - todo
* add new VyoS instances test connection while adding - todo
* add new VyoS instances test connection all servers crontab - todo
* associate groups to VyOS instances

### known issues
* cannot edit firewall rules number using current API


# dockerhub
latest VyControl is being autobuilt at dockerhub https://hub.docker.com/r/robertoberto/vycenter
```
docker pull robertoberto/vycenter
```

# docker composer

Right now we are using db.sqlite3, but I used composer so we can change to mySQL if needed.

```
docker-compose build
docker-compose  up
```

# manual install instructions

## setup virtual env and pip requirements
```
virtualenv env
source env/bin/activate
pip3 install -r requirements.txt
```

## setup initial database
```
cd vycenter
python3 manage.py migrate
```

## run webserver
```
python3 manage.py runserver
```

## access webpage
http://127.0.0.1:8000/


## setup vyos new instance
* click on *Add new instance*
* configure vyos services like explained here https://docs.vyos.io/en/latest/appendix/http-api.html
* click on *List Instances*
* click on *Test Connection*

# references
* https://docs.vyos.io/en/latest/appendix/http-api.html
* https://forum.vyos.io/t/http-api-for-show/3922
* https://blog.vyos.io/vyos-rolling-release-has-got-an-http-api 

# screenshoots (keep in mind we're in early alpha stages)

## List VyOS Instances
![List VyOS Instances](https://storage.googleapis.com/imgvycenter/screenshoot-alfa1/list-instances.png)

## Add VyOS Instances
![Add VyOS Instances](https://storage.googleapis.com/imgvycenter/screenshoot-alfa1/add-instance.png)

## List Interfaces
![List Interfaces](https://storage.googleapis.com/imgvycenter/screenshoot-alfa1/list-interfaces.png)

## Firewall Dashboard
![Firewall Dashboard](https://storage.googleapis.com/imgvycenter/screenshoot-alfa1/firewall-dash.png)

## Add Firewall Rule
![Add Firewall Rule](https://storage.googleapis.com/imgvycenter/screenshoot-alfa1/firewall-rule.png)


