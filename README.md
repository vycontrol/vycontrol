# VyControl

<p align="center">
<img align="center" width="150" height="150" src="https://storage.googleapis.com/vycontrol/logos/logo_transparent.png">
</p>


VyControl is a single frontend interface to manage a single or multiple VyoS servers. Only download [VyOS](https://www.vyos.io/) Rolling Release, since VyControl needs the latest VyOS API.


Still in 2020, the most important functionalities that until then were only possible through CLI (command line interface), will be possible through a friendly web interface developed in Django / Python.

Standalone VyoS installations can now have a control panel.

Datacenter installations with multiple VyoS will be able to offer their customers (with users, groups and granular control) firewall as a service.



# Main links

* [VyControl](https://www.vycontrol.com/) website
* [VyOS](https://www.vyos.io/) linux firewall website (only compatible with rolling release / 1.3 VyOS)
* [Reddit](https://www.reddit.com/r/vycontrol/) 

# Plan to use VyControl?
- [ ] **Subscribe to our announce list** at https://vycontrol.com/
- [ ] Join Slack Channel https://vycontrol.slack.com/archives/C012ZRMB8VB
- [ ] Add new enhancement requests at https://github.com/vycontrol/vycontrol/issues

# Plan to develop VyControl?
- [ ] Solve Issues at https://github.com/vycontrol/vycontrol/issues
- [ ] Forks and pull requests are welcome!
- [ ] Discussion VyControl at VyOS forum https://forum.vyos.io/t/vycenter-alpha-stage-announcement-vyos-web-interface/5221/4

# roadmap 

## current version 
- [x] [20.05.10 - zone based firewall](https://github.com/vycontrol/vycontrol/milestone/13)

## changelog
- [x] [20.05.04 - improve firewall UI and error returns to end users](https://github.com/vycontrol/vycontrol/milestone/17)
- [x] 20.05.02 - working firewall without zones 
- [x] 20.05.01 - version created to start project framework, organize permission systems and concept test with some firewall and interface functions and statics routes

## future versions

### firewall and vycontrol base   
- [ ] [improve users/group/profile crud](https://github.com/vycontrol/vycontrol/milestones/16)
- [ ] [lost password recovery](https://github.com/vycontrol/vycontrol/milestone/11)
- [ ] [layout improvements and user input validation](https://github.com/vycontrol/vycontrol/milestone/5)

### IPSEC / OpenVPN focus 
- [ ] [openvpn features](https://github.com/vycontrol/vycontrol/milestone/8)
- [ ] [ipsec features](https://github.com/vycontrol/vycontrol/milestone/8)
- [ ] [Finish some firewall options](https://github.com/vycontrol/vycontrol/milestone/15)

## vlans, interfaces and system users
- [ ] [system ssh / logins config](https://github.com/vycontrol/vycontrol/milestone/12)
- [ ] [basic interfaces configuration and vlans](https://github.com/vycontrol/vycontrol/milestone/10)
- [ ] [host information and default gateway](https://github.com/vycontrol/vycontrol/milestone/12)
- [ ] [timezone / ntp](https://github.com/vycontrol/vycontrol/milestone/12)

### basic dynamic routing features
- [ ] [OSPF features](https://github.com/vycontrol/vycontrol/milestone/14)

### addons features 
- [ ] [FastNetMon one-click integration](https://github.com/vycontrol/vycontrol/milestone/19)
- [ ] [save/commit/load features](https://github.com/vycontrol/vycontrol/milestone/18)
- [ ] [s3 backup scheduler and commit confirm](https://github.com/vycontrol/vycontrol/milestone/4)
- [ ] [granular permissions and improvements](https://github.com/vycontrol/vycontrol/milestone/1)
- [ ] [commit, save, load config](https://github.com/vycontrol/vycontrol/milestone/3)

### advanced dynamic routing features
- [ ] [BGP features](https://github.com/vycontrol/vycontrol/milestone/14)

### IPV6 features
- [ ] [ipv6 milestone](https://github.com/vycontrol/vycontrol/milestone/6)

### other features
- [ ] [other features or dependencies](https://github.com/vycontrol/vycontrol/milestone/9)

### versions convention

Note that versions numbers are not related to dates.
* major eg 20
  * minor eg 05
    * feature eg 05
       * build eg 1010

Will give 20.05.05.1010

## lifecycle
* initially LTS (Long Term Support) versions will be supported by 6 months just to bugfixes
* in the future we will extend the time span of LTS versions


# installation 

* for your security edit SECRET_KEY in inside Django settings.py and change to something random, maybe using 
```
openssl rand -hex 32
```


## by dockerhub
latest VyControl is being autobuilt at dockerhub https://hub.docker.com/r/robertoberto/vycontrol
```
docker pull robertoberto/vycontrol
docker run -p 8000:8000 -t robertoberto/vycontrol
access http://127.0.0.1:8000
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
cd vycontrol
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
* https://www.facebook.com/VyControl-101048288289351


# screenshoots 

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
