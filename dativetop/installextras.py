import logging
import os
import shlex
import shutil
import subprocess
import sys

from dativetop.getsettings import get_settings
import dativetop.logging


logger = logging.getLogger(__name__)


def get_core_paths(app_dir):
    """Return the core paths in the target app directory: src/, src/old/,
    src/dative/, and src/old/store/.
    """
    src_pth = os.path.join(app_dir, 'src')
    old_pth = os.path.join(src_pth, 'old')
    dative_pth = os.path.join(src_pth, 'dative')
    old_store_pth = os.path.join(old_pth, 'store')
    return src_pth, old_pth, dative_pth, old_store_pth


def create_paths(*paths):
    """Create the core paths in the target app directory: src/, src/old/,
    src/dative/, and src/old/store/.
    """
    for pth in paths:
        if not os.path.exists(pth):
            os.makedirs(pth)
    logger.info('Created source directories under %s.', paths[0])


def copy_private_resources(app_dir):
    """Copy DativeTop's private_resources/ directory to the analogous location
    in the target app.
    """
    private_resources_src_pth = os.path.join('dativetop', 'private_resources')
    private_resources_dst_pth = os.path.join(
        app_dir, 'dativetop', 'private_resources')
    if os.path.exists(private_resources_dst_pth):
        shutil.rmtree(private_resources_dst_pth)
    shutil.copytree(private_resources_src_pth, private_resources_dst_pth)
    logger.info('Copied DativeTop private resources to %s.', private_resources_dst_pth)


def copy_dative_build(app_dir):
    """Copy the built Dative app (minified JavaScript) to the target app.
    """
    dative_src_pth = os.path.join('src', 'dative', 'dist')
    dative_dst_pth = os.path.join(app_dir, 'src', 'dative', 'dist')
    if os.path.exists(dative_dst_pth):
        shutil.rmtree(dative_dst_pth)
    shutil.copytree(dative_src_pth, dative_dst_pth)
    logger.info('Copied Dative build to %s.', dative_dst_pth)


OLD_CONFIG_KEYS_TO_DATIVETOP_CONFIG_KEYS = {
    'permanent_store': 'old_permanent_store',
    'db.rdbms': 'old_db_rdbms',
    'session.type': 'old_session_type'
}


def process_config_line(line, settings):
    """If ``line`` assigns a value to one of the keys in
    ``OLD_CONFIG_KEYS_TO_DATIVETOP_CONFIG_KEYS``, then replace it with an
    assignment that sets the value to the settings value of the matching key in
    ``OLD_CONFIG_KEYS_TO_DATIVETOP_CONFIG_KEYS``.
    """
    for k, v in OLD_CONFIG_KEYS_TO_DATIVETOP_CONFIG_KEYS.items():
        if line.startswith(f'{k} ='):
            return f'{k} = {settings[v]}\n'
    return line


def write_old_config(app_dir, settings):
    """Write a DativeTop-specific OLD config.ini file into the target app.

    It is a copy of the source OLD config.ini with certain lines changed to
    reflect the DativeTop deploy. The changes tell the OLD where its store/
    directory is, what kind of RDBMS it is using (SQLite), and that the session
    type is "file". See ``OLD_CONFIG_KEYS_TO_DATIVETOP_CONFIG_KEYS``.
    """
    old_cfg_src_pth = os.path.join('src', 'old', 'config.ini')
    old_cfg_dst_pth = os.path.join(app_dir, 'src', 'old', 'config.ini')
    with open(old_cfg_src_pth) as fi:
        with open(old_cfg_dst_pth, 'w') as fo:
            for line in fi:
                fo.write(process_config_line(line, settings))
    logger.info('Wrote OLD config file to %s.', old_cfg_dst_pth)


def copy_old_directory_structure(settings, old_store_pth):
    """Recursively copy the OLD default app's directory structure under store/
    into the target app.
    """
    old_instance_src_dir = os.path.join(
        settings['old_permanent_store'],
        settings['dflt_dativetop_old_name'])
    old_instance_dst_dir = os.path.join(
        old_store_pth,
        settings['dflt_dativetop_old_name'])
    if os.path.exists(old_instance_dst_dir):
        shutil.rmtree(old_instance_dst_dir)
    shutil.copytree(old_instance_src_dir, old_instance_dst_dir)
    logger.info('Copied OLD directory structure from %s to %s.',
                old_instance_src_dir, old_instance_dst_dir)


def copy_old_database(settings, old_pth):
    """Copy the OLD SQLite database file into the target app."""
    old_db_file_name = '{}.sqlite'.format(settings['dflt_dativetop_old_name'])
    old_db_src = os.path.join(
        settings['old_db_dirpath'],  # = oldinstances/dbs/
        old_db_file_name)
    old_db_dst = os.path.join(
        old_pth,  # = src/old/
        old_db_file_name)
    if os.path.exists(old_db_dst):
        os.remove(old_db_dst)
    shutil.copyfile(old_db_src, old_db_dst)
    logger.info('Copied OLD database file from %s to %s.', old_db_src,
                old_db_dst)


def install_old(app_dir):
    """Install the OLD's Python dependencies into the target app."""
    cmds = (
        (f'pip install'
         f' --upgrade'
         f' --force-reinstall'
         f' --target={app_dir}'
         f' -r src/old/requirements/testsqlite.txt'),
        'python src/old/setup.py develop',
    )
    for cmd in cmds:
        logger.info('Running command: ``%s``.', cmd)
        p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)
        while True:
            output = p.stdout.readline()
            if output == b'' and p.poll() is not None:
                break
            if output:
                logger.info(output.decode('utf8').strip())
        rc = p.poll()
        logger.info('Command exited with status code %s.', rc)
    logger.info('Installed the OLD.')


def install_extras(self):
    """Override for Briefcase's ``install_extras`` method. In summary, it
    copies the source files of Dative and the OLD to the target Briefcase app
    and installs Python dependencies in that app for the OLD.
    """
    settings = get_settings(config_path=self.dativetop_config_path)
    src_pth, old_pth, dative_pth, old_store_pth = get_core_paths(self.app_dir)
    create_paths(src_pth, old_pth, dative_pth, old_store_pth)
    copy_private_resources(self.app_dir)
    copy_dative_build(self.app_dir)
    write_old_config(self.app_dir, settings)
    copy_old_directory_structure(settings, old_store_pth)
    copy_old_database(settings, old_pth)
    install_old(self.app_dir)
