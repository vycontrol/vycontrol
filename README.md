<p align="center">
<img align="center" width="150" height="30" src="https://storage.googleapis.com/vycontrol/logos/logotxt.png" alt="VyControl">
</p>


VyControl is frontend interface to manage a single or multiple VyoS servers. 

Datacenters can to offer their customers (with users, groups and granular control) firewall and router as a service.


# Main links

* [VyControl](https://www.vycontrol.com/) website
* [VyOS](https://www.vyos.io/) linux firewall website (only compatible with rolling release / 1.3 VyOS)
* [Reddit](https://www.reddit.com/r/vycontrol/) 

# Plan to use VyControl?
- [ ] **Subscribe to our announce list** at https://vycontrol.com/
- [ ] Join Slack Channel https://vycontrol.slack.com/archives/C012ZRMB8VB
- [ ] Add new enhancement requests at https://github.com/vycontrol/vycontrol/issues

# Install instructions 

* download [VyOS](https://www.vyos.io/) Rolling Release, since VyControl needs the latest VyOS API.
* for your security edit SECRET_KEY in inside Django settings/production.py and change to something random, maybe using 
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

## setup email provider
VyControl send email to users when they click on Forget Password. So you need to setup a email provider to be able to use this features.

* edit vycontrol/settings/production.py
* change according your mail provider, you can use gmail accounts, sendergrid, amazon ses, mailgun etc
```
EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'user'
EMAIL_HOST_PASSWORD = 'password'
EMAIL_USE_TLS = True
```

# Plan to help develop VyControl?
- [ ] Solve Issues at https://github.com/vycontrol/vycontrol/issues
- [ ] Forks and pull requests are welcome!
- [ ] Discussion VyControl at VyOS forum https://forum.vyos.io/t/vycenter-alpha-stage-announcement-vyos-web-interface/5221/4

# changelog
- [x] change email/change password user profile
- [x] edit/add/delete interfaces
- [x] lost password recovery using external SMTP server
- [x] NTP servers add/list/delete
- [x] zone based firewall
- [x] improve firewall UI and error returns to end users
- [x] working firewall without zones 
- [x] version created to start project framework, organize permission systems and concept test with some firewall and interface functions and statics routes

# roadmap

## firewall and vycontrol base   
- [ ] improve users/group/profile crud
- [ ] layout improvements and user input validation
- [ ] use python logging

## IPSEC / OpenVPN focus 
- [ ] openvpn features
- [ ] ipsec features
- [ ] Finish some firewall options

## vlans, interfaces and system users
- [ ] system ssh / logins config
- [ ] basic interfaces configuration and vlans
- [ ] host information and default gateway
- [ ] timezone

## basic dynamic routing features
- [ ] OSPF features

## addons features 
- [ ] FastNetMon one-click integration
- [ ] save/commit/load features
- [ ] s3 backup scheduler and commit confirm
- [ ] granular permissions and improvements

## advanced dynamic routing features
- [ ] BGP features

## IPV6 features
- [ ] ipv6 milestone

# references
* https://docs.vyos.io/en/latest/appendix/http-api.html
* https://forum.vyos.io/t/http-api-for-show/3922
* https://blog.vyos.io/vyos-rolling-release-has-got-an-http-api 
* https://www.facebook.com/vycontrol


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
