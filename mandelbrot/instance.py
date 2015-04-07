import os
import pathlib
import logging
import lockfile
import sqlite3
import tempfile

log = logging.getLogger("mandelbrot.instance")

class Instance(object):
    """
    """
    def __init__(self, path):
        """
        :param path:
        :type path: pathlib.Path
        """
        self.path = path
        self._db = None

    @property
    def conn(self):
        if self._db is None:
            self._db = sqlite3.connect(str(self.path / 'db'))
        return self._db

    def close(self):
        if self._db is not None:
            self._db.close()
        self._db = None

    def lock(self):
        lock_path = str(self.path / 'lock')
        return lockfile.LockFile(lock_path, threaded=True)

    def initialize(self):
        with self.conn as conn:
            conn.execute(_SQLStatements.create_version_table)
            conn.execute(_SQLStatements.create_v1_agent_id_table)
            conn.execute(_SQLStatements.create_v1_endpoint_url_table)
            conn.execute(_SQLStatements.create_v1_check_table)
            conn.execute(_SQLStatements.create_v1_metadata_table)
            cursor = conn.cursor()
            cursor.execute(_SQLStatements.get_version)
            version_number = cursor.fetchone()
            if version_number is None:
                cursor.execute(_SQLStatements.set_version, (_SQLStatements.version,))
            elif version_number[0] != _SQLStatements.version:
                raise Exception("wrong version")
            else:
                pass

    def get_agent_id(self):
        with self.conn as conn:
            cursor = conn.cursor()
            cursor.execute(_SQLStatements.get_agent_id)
            results = cursor.fetchone()
            if results is not None:
                return results[0]
            return None

    def set_agent_id(self, agent_id):
        with self.conn as conn:
            conn.execute(_SQLStatements.set_agent_id, (agent_id,))

    def get_endpoint_url(self):
        with self.conn as conn:
            cursor = conn.cursor()
            cursor.execute(_SQLStatements.get_endpoint_url)
            results = cursor.fetchone()
            if results is not None:
                return results[0]
            return None

    def set_endpoint_url(self, endpoint_url):
        with self.conn as conn:
            conn.execute(_SQLStatements.set_endpoint_url, (endpoint_url,))

    def list_checks(self):
        with self.conn as conn:
            cursor = conn.cursor()
            cursor.execute(_SQLStatements.list_checks)
            for check_id, check_type, check_params, delay, offset, jitter in cursor.fetchall():
                yield InstanceCheck(check_id, check_type, check_params, delay, offset, jitter)

    def get_check(self, check_id):
        with self.conn as conn:
            cursor = conn.cursor()
            cursor.execute(_SQLStatements.get_check, (check_id,))
            results = cursor.fetchone()
            if results is not None:
                check_id, check_type, check_params, delay, offset, jitter = results
                return InstanceCheck(check_id, check_type, check_params, delay, offset, jitter)
            return None

    def set_check(self, instance_check):
        with self.conn as conn:
            conn.execute(_SQLStatements.set_check, (instance_check.check_id,
                instance_check.check_type, instance_check.check_params, instance_check.delay,
                instance_check.offset, instance_check.jitter))

    def delete_check(self, check_id):
        with self.conn as conn:
            conn.execute(_SQLStatements.delete_check, (check_id,))

class InstanceCheck(object):
    """
    """
    def __init__(self, check_id, check_type, check_params, delay, offset, jitter):
        """
        """
        self.check_id = check_id
        self.check_type = check_type
        self.check_params = check_params
        self.delay = delay
        self.offset = offset
        self.jitter = jitter

class _SQLStatements(object):
    """
    """

    version = 1

    create_version_table = """
CREATE TABLE IF NOT EXISTS version ( version_number INTEGER );
"""

    create_v1_agent_id_table = """
CREATE TABLE IF NOT EXISTS v1_agent_id ( agent_id TEXT );
"""

    create_v1_endpoint_url_table = """
CREATE TABLE IF NOT EXISTS v1_endpoint_url ( endpoint_url TEXT );
"""
    create_v1_check_table = """
CREATE TABLE IF NOT EXISTS v1_check (
    check_id TEXT PRIMARY KEY,
    check_type TEXT,
    check_params TEXT,
    delay INTEGER,
    offset INTEGER,
    jitter INTEGER
);
"""

    create_v1_metadata_table = """
CREATE TABLE IF NOT EXISTS v1_metadata (
    check_id TEXT PRIMARY KEY,
    name TEXT,
    value TEXT
);
"""

    get_version = "SELECT version_number FROM version WHERE rowid=0;"

    set_version = "INSERT OR REPLACE INTO version ( rowid, version_number ) VALUES ( 0, ? );"

    get_agent_id = "SELECT agent_id from v1_agent_id WHERE rowid=0;"

    set_agent_id = "INSERT OR REPLACE INTO v1_agent_id ( rowid, agent_id ) VALUES ( 0, ? );"

    get_endpoint_url = "SELECT endpoint_url from v1_endpoint_url WHERE rowid=0;"

    set_endpoint_url = "INSERT OR REPLACE INTO v1_endpoint_url ( rowid, endpoint_url ) VALUES ( 0, ? );"

    list_checks = "SELECT check_id, check_type, check_params, delay, offset, jitter FROM v1_check;"

    get_check = "SELECT check_id, check_type, check_params, delay, offset, jitter FROM v1_check WHERE check_id=?;"

    set_check = "INSERT OR REPLACE INTO v1_check (check_id, check_type, check_params, delay, offset, jitter) VALUES ( ?, ?, ?, ?, ?, ?);"

    delete_check = "DELETE FROM v1_check WHERE check_id=?;"

def create_instance(path):
    """
    :param path:
    :type path: pathlib.Path
    :return:
    """
    if path.exists():
        raise Exception("failed to create instance {0}: instance exists".format(path))
    # create a secure temporary directory
    temp_dir = tempfile.mkdtemp(prefix=".{0}.".format(path.name), dir=str(path.parent))
    # initialize the instance inside the temp_dir
    instance = Instance(pathlib.Path(temp_dir))
    instance.initialize()
    instance.close()
    # move the temp dir into place
    os.rename(str(temp_dir), str(path))
    return Instance(path)

def open_instance(path):
    """
    :param path:
    :type path: pathlib.Path
    :return:
    """
    if not path.exists():
        raise Exception("failed to open instance {0}: instance doesn't exist".format(path))
    return Instance(path)
