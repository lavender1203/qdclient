#cd /etc/yum.repos.d/
#mv CentOS-Base.repo CentOS-Base.repo.back
#wget -O CentOS-Base.repo http://mirrors.aliyun.com/repo/Centos-6.repo
#yum clean all
#yum makecache
#cd -
yum install -y yum-utils device-mapper-persistent-data lvm2
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
yum install -y docker-ce docker-ce-cli containerd.io
echo -e "{\n    \"registry-mirrors\": [\"https://7uuu3esz.mirror.aliyuncs.com\"]\n}\n" > /etc/docker/daemon.json
systemctl restart docker
docker pull mysql
docker run -d -p 3306:3306 --name mysql -v /etc/mysql/conf.d:/etc/mysql/conf.d -v /etc/mysql/logs:/logs -v /etc/mysql/data:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=toor mysql:latest
# 映射copy文件路径到docker容器
#docker cp /root/qdclient/docker_mysql_create_table.sh mysql:/docker_mysql_create_table.sh
#docker exec -it mysql  /bin/bash -c "sh /docker_mysql_create_table.sh"
chkconfig docker on
firewall-cmd --zone=public --add-port=3306/tcp --permanent
firewall-cmd --reload
pip3 install -i https://mirrors.aliyun.com/pypi/simple/ flask
pip3 install -i https://mirrors.aliyun.com/pypi/simple/ requests
# yum -y install python36-devel libevent-devel libjpeg-devel zlib-devel
yum -y install autoconf
yum -y install xz-devel zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel libffi-devel gcc make
cd /root/qdclient/backend/install/Python-3.7.6
make distclean
./configure --enable-optimizations --enable-shared && make && make install
ln -s /usr/local/bin/python3.7 /usr/bin/python3
pip3 install --upgrade pip
cd -
pip3 install -i https://mirrors.aliyun.com/pypi/simple/ cryptography
pip3 install -i https://mirrors.aliyun.com/pypi/simple/ setuptools
pip3 install -i https://mirrors.aliyun.com/pypi/simple/ gevent 
pip3 install -i https://mirrors.aliyun.com/pypi/simple/ pycrypto
pip3 install -i https://mirrors.aliyun.com/pypi/simple/ fake_useragent
pip3 install -i https://mirrors.aliyun.com/pypi/simple/ selenium
pip3 install -i https://mirrors.aliyun.com/pypi/simple/ pillow 
pip3 install -i https://mirrors.aliyun.com/pypi/simple/ pymysql 
pip3 install -i https://mirrors.aliyun.com/pypi/simple/ uvloop 
pip3 install -i https://mirrors.aliyun.com/pypi/simple/ asyncio 
pip3 install -i https://mirrors.aliyun.com/pypi/simple/ flask_cors
pip3 install -i https://mirrors.aliyun.com/pypi/simple/ redis
pip3 install -i https://mirrors.aliyun.com/pypi/simple/ DBUtils 
pip3 install -i https://mirrors.aliyun.com/pypi/simple/ matplotlib
pip3 install -i https://mirrors.aliyun.com/pypi/simple/ opencv-python
yum -y install libSM-1.2.2-2.el7.x86_64 --setopt=protected_multilib=false
yum -y install libXext-1.3.3-3.el7.x86_64 --setopt=protected_mul
yum -y install libXrender-0.9.10-1.el7.x86_64 --setopt=protected
pip3 install -i https://mirrors.aliyun.com/pypi/simple/ pandas
pip3 install -i https://mirrors.aliyun.com/pypi/simple/ uwsgi
touch /etc/yum.repos.d/nginx.repo
echo -e "[nginx]\nname=nginx-repo\nbaseurl=http://nginx.org/packages/centos/7/\x24basearch/\ngpgcheck=0\nenabled=1\n" > /etc/yum.repos.d/nginx.repo
yum -y install nginx
firewall-cmd --zone=public --add-port=8080/tcp --permanent 
systemctl restart firewalld.service
firewall-cmd --reload
touch /etc/nginx/conf.d/qidian.conf
echo -e "server {\n    listen 80;\n    server_name localhost;\n    location / {\n        include uwsgi_params;\n        uwsgi_pass 192.168.2.120:8080;\n    }\n}\n" > /etc/nginx/conf.d/qidian.conf
uwsgi --reload -d --ini uwsgi.ini 
systemctl restart nginx
#wget http://repo.mysql.com/mysql-community-release-el7-5.noarch.rpm
#rpm -ivh mysql-community-release-el7-5.noarch.rpm
#yum -y install mysql-server
cd backend/install
tar -xvf node-v12.15.0-linux-x64.tar.xz
cd -
ln -s /root/qdclient/backend/install/node-v12.15.0-linux-x64/bin/node /usr/bin/node
ln -s /root/qdclient/backend/install/node-v12.15.0-linux-x64/bin/npm /usr/bin/npm
yum install -y epel-release
yum install -y chromium
cp /root/qdclient/backend/chrome/79/chromedriver /usr/bin/
yum install -y redis
echo -e "requirepass Winnie@901029" >> /etc/redis.conf
systemctl restart redis
