import os


def introspect_old_instances(dativetop_settings):
    """Return a list of OLD instance dicts, deduced by inspecting the
    .sqlite files listed under ``config['old_db_dirpath']``. Aside from the
    defaults, the file system data gives us the name and local URL of each
    instance.
    """
    old_instances = []
    old_db_dirpath = dativetop_settings.get('old_db_dirpath')
    if old_db_dirpath and os.path.isdir(old_db_dirpath):
        for e_name in os.listdir(old_db_dirpath):
            e_path = os.path.join(old_db_dirpath, e_name)
            if os.path.isfile(e_path):
                old_name, ext = os.path.splitext(e_name)
                if ext == '.sqlite':
                    old_instances.append(
                        {'local_path': e_path, 'db_file_name': old_name})
    return old_instances
