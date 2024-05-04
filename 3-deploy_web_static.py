#!/usr/bin/python3
"""
Fabric script for deploying web_static content to web servers.

Usage: fab -f 3-deploy_web_static.py deploy -i /root/.ssh/school -u ubuntu
"""

from fabric.api import env, local, put, run
from datetime import datetime
from os.path import exists, isdir

# Configure Fabric environment
env.user = 'ubuntu'
env.key_filename = '/root/.ssh/school'
env.hosts = ['100.25.153.16', '100.25.156.205']


def do_pack():
    """Generates a compressed archive of web_static directory."""
    try:
        date = datetime.now().strftime("%Y%m%d%H%M%S")
        if not isdir("versions"):
            local("mkdir -p versions")
        file_name = "versions/web_static_{}.tgz".format(date)
        local("tar -cvzf {} web_static".format(file_name))
        return file_name
    except Exception as e:
        print("Error in packaging: {}".format(e))
        return None


def do_deploy(archive_path):
    """Distributes an archive to the web servers and sets up symbolic link."""
    if not exists(archive_path):
        print("Archive not found: {}".format(archive_path))
        return False
    try:
        file_name = archive_path.split("/")[-1]
        no_ext = file_name.split(".")[0]
        path = "/data/web_static/releases/"
        put(archive_path, '/tmp/')
        run('mkdir -p {}{}/'.format(path, no_ext))
        run('tar -xzf /tmp/{} -C {}{}/'.format(file_name, path, no_ext))
        run('rm /tmp/{}'.format(file_name))
        run('mv {0}{1}/web_static/* {0}{1}/'.format(path, no_ext))
        run('rm -rf {}{}/web_static'.format(path, no_ext))
        run('rm -rf /data/web_static/current')
        run('ln -s {}{}/ /data/web_static/current'.format(path, no_ext))
        return True
    except Exception as e:
        print("Error in deployment: {}".format(e))
        return False


def deploy():
    """Main deployment function that creates and distributes the archive."""
    archive_path = do_pack()
    if archive_path:
        return do_deploy(archive_path)
    else:
        return False

