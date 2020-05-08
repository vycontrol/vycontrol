# VyControl
* [VyOS](https://www.vyos.io/) frontend made in Python / Django using VyOS new 1.3 API server
* Check out website at https://www.vycontrol.com/


<p align="center">
<img align="center" width="150" height="150" src="https://storage.googleapis.com/vycontrol/logos/logo_transparent.png">
</p>



It will work with a single VyoS server or to multiple VyOS servers, so datacenters which do not want share same firewall to different customers will not need to install several VyControl to each customer. That's why the name VyControl.

## community
* Slack Channel https://vycontrol.slack.com/archives/C012ZRMB8VB
* Forum Post https://forum.vyos.io/t/vycenter-alpha-stage-announcement-vyos-web-interface/5221/4

## roadmap versions

### active develpment version
* 20.05.01 - version created to start project framework, organize permission systems and concept test with some firewall and interface functions and statics routes - software work as a proof of concept **almost done**

### future vesions
* 20.05.02 - working firewall without zones bases firewall - software work for whom want firewall without zones
* 20.05.03 - zone based firewall
* 20.05.04 - IPSEC features
* 20.05.05 - better html css - someone help please :-)
* 20.06.01 - save/commit/load features and ssh / logins 
* 20.06.02 - vlans / interfaces deep configuration
* 20.06.03 - improve permissions to allow users inside same group to have different roles


# installation 

## by dockerhub
latest VyControl is being autobuilt at dockerhub https://hub.docker.com/r/robertoberto/vycontrol
```
docker pull robertoberto/vycontrol
```

## by docker composer

Right now we are using db.sqlite3, but I used composer so we can change to mySQL if needed.

```
docker-compose build
docker-compose  up
```

## manual install instructions

### setup virtual env and pip requirements
```
virtualenv env
source env/bin/activate
pip3 install -r requirements.txt
```

### setup initial database
```
cd vycenter
python3 manage.py migrate
```

### run webserver
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

## Install VyControl
![Install VyControl](https://storage.googleapis.com/vycontrol/screenshoots/20.05.01/install.png)

## List Users
![List Users](https://storage.googleapis.com/vycontrol/screenshoots/20.05.01/list_users.png)

## List VyOS Instances
![List VyOS Instances](https://storage.googleapis.com/vycontrol/screenshoots/20.05.01/list_instances.png)

## Add VyOS Instances
![Add VyOS Instances](https://storage.googleapis.com/vycontrol/screenshoots/20.05.01/add_instance.png)
                      
## List Interfaces
![List Interfaces](https://storage.googleapis.com/vycontrol/screenshoots/20.05.01/list_instances.png)

## List Firewall
![List Dashboard](https://storage.googleapis.com/vycontrol/screenshoots/20.05.01/list_firewall.png)

## Add Firewall Rule
![Add Firewall Rule](https://storage.googleapis.com/vycontrol/screenshoots/20.05.01/add_firewall_rule.png)

## List Static Routes
![List Static Routes](https://storage.googleapis.com/vycontrol/screenshoots/20.05.01/list_static.png)


# Sponsoring
* VyControl is being tested at [Under](https://under.com.br) a Brazilian provider of Cloud Computing and Datacenters.
