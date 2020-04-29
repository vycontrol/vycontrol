# vycenter
VyOS frontend made in Python / Django using VyOS new 1.3 API server

It will work with a single VyoS server or to multiple VyOS servers, so datacenters which do not want share same firewall to different customers will not need to install several vycenter to each customer. That's why the name vycenter.

## features
in alpha stage we're going to provide just essential device config, interfaces and firewall, as proof of concencept, as well config module basic cruds (users, groups and vyOS Servers)

### device module
* list interfaces - alpha
* show interface - alpha
* unset/set firewall interface - todo
* change interface parameters - todo
* crud firewall - todo
* use VyOS instances from database not local.py - todo

### config module
* users crud - todo
* groups crud - todo
* add new VyoS instances only db work - alpha
* add new VyoS instances test connection while adding - todo
* add new VyoS instances test connection all servers - todo
* associate groups to VyOS instances

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


