#Graduation Project 2
This is my Graducation Project repository.
Data visualization system starting from [gatherplot](https://github.com/intuinno/gatherplot).
You can find development journey at [here](http://ryoo.kr/tag/gp2)(korean).

##How to run?
###For server
1. You need [python](https://www.python.org/)>=2.7.x for server and [node](https://nodejs.org)>=6.9.x for client
2. Install [virtualenv](https://virtualenv.pypa.io/en/stable) for convience. `pip install virtualenv`
3. Create [virtualenv](https://virtualenv.pypa.io/en/stable) by typing `virtualenv venv`
4. Activate [virtualenv](https://virtualenv.pypa.io/en/stable) by typing `. venv/bin/activate`(or `.\venv\Scripts\activate` on Windows)
5. Install dependencies by typing `pip install -e .` or `python setup.py install`
6. You can use [gunicorn](http://gunicorn.org/) if you are not on Windows. Type `cd gp2-core` and type `gunicorn app:app -b 0.0.0.0:8888`. You can see your site at http://localhost:8888.
7. If you are on Windows, you need to set Environmnet Variable FLASK_APP in My Computer and run `flask run`. You can see your site at http://localhost:5000.
###For client
Coming Soon :)

##How to Deploy?
I utilize [Fabric](https://get.fabric.io/) to deploy python app at remote machine. Code is tested from Windows 10 to Ubuntu 16.04 machine with following settings
 - account that can access instance by ssh with password
 - /www directory with write permission
 - nginx, supervisor, python, pip(python-pip), virtualenv(python-virtualenv) should be installed. starting nginx and supervisor at boot is also recommended.
You need to install dev packages to use deploy code. type `pip install -e .[dev]` for installing required packages.
###First Deployment
`fab init_deploy` should do all the work. However you should keep an eye on variables like VHOST, because it should be changed.
###Update
`fab deploy` should update code from *github repository*. You need to commit before deployment!

## License

© Yangwook Ryoo, 2017. Licensed under an [MIT](LICENSE) license.
