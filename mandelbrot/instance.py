import os
import pathlib
import urllib.parse
import logging
import lockfile
import sqlite3
import tempfile
import json
import cifparser

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
            conn.execute(_SQLStatements.create_v1_manifest_url_table)
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
                return cifparser.make_path(results[0])
            return None

    def set_agent_id(self, agent_id):
        assert isinstance(agent_id, cifparser.Path)
        with self.conn as conn:
            conn.execute(_SQLStatements.set_agent_id, (str(agent_id),))

    def get_manifest_url(self):
        with self.conn as conn:
            cursor = conn.cursor()
            cursor.execute(_SQLStatements.get_manifest_url)
            results = cursor.fetchone()
            if results is not None:
                return str(results[0])
            return None

    def set_manifest_url(self, manifest_url):
        with self.conn as conn:
            conn.execute(_SQLStatements.set_manifest_url, (manifest_url,))

    def get_endpoint_url(self):
        with self.conn as conn:
            cursor = conn.cursor()
            cursor.execute(_SQLStatements.get_endpoint_url)
            results = cursor.fetchone()
            if results is not None:
                return urllib.parse.urlparse(results[0])
            return None

    def set_endpoint_url(self, endpoint_url):
        with self.conn as conn:
            conn.execute(_SQLStatements.set_endpoint_url,
                (urllib.parse.urlunparse(endpoint_url),))

    def list_metadata(self):
        with self.conn as conn:
            cursor = conn.cursor()
            cursor.execute(_SQLStatements.list_metadata)
            results = cursor.fetchall()
        for meta_name, meta_value in results:
            yield (str(meta_name), str(meta_value))

    def get_meta_value(self, meta_name):
        with self.conn as conn:
            cursor = conn.cursor()
            cursor.execute(_SQLStatements.get_meta_value, (meta_name,))
            results = cursor.fetchone()
            if results is not None:
                return str(results[0])
            return None

    def set_meta_value(self, meta_name, meta_value):
        with self.conn as conn:
            conn.execute(_SQLStatements.set_meta_value, (meta_name, meta_value))

    def delete_meta_value(self, meta_name):
        with self.conn as conn:
            conn.execute(_SQLStatements.delete_meta_value, (meta_name,))

    def flush_metadata(self):
        with self.conn as conn:
            conn.execute(_SQLStatements.flush_metadata)

    def list_checks(self):
        with self.conn as conn:
            cursor = conn.cursor()
            cursor.execute(_SQLStatements.list_checks)
            results = cursor.fetchall()
        for check_id, check_type, check_params, delay, offset, jitter in results:
            check_id = cifparser.make_path(check_id)
            check_type = str(check_type)
            check_params = cifparser.Namespace(cifparser.load(json.loads(check_params)))
            delay = float(delay)
            offset = float(offset)
            jitter = float(jitter)
            yield InstanceCheck(check_id, check_type, check_params, delay, offset, jitter)

    def get_check(self, check_id):
        with self.conn as conn:
            cursor = conn.cursor()
            cursor.execute(_SQLStatements.get_check, (check_id,))
            results = cursor.fetchone()
            if results is not None:
                check_id = cifparser.make_path(results[0])
                check_type = str(results[1])
                check_params = cifparser.Namespace(cifparser.load(json.loads(results[2])))
                delay = float(results[3])
                offset = float(results[4])
                jitter = float(results[5])
                return InstanceCheck(check_id, check_type, check_params, delay, offset, jitter)
            return None

    def set_check(self, instance_check):
        with self.conn as conn:
            check_id = str(instance_check.check_id)
            check_type = str(instance_check.check_type)
            check_params = json.dumps(cifparser.dump(instance_check.check_params.values))
            delay = float(instance_check.delay)
            offset = float(instance_check.offset)
            jitter = float(instance_check.jitter)
            conn.execute(_SQLStatements.set_check, (check_id, check_type,
                check_params, delay, offset, jitter))

    def delete_check(self, check_id):
        with self.conn as conn:
            conn.execute(_SQLStatements.delete_check, (check_id,))

    def flush_checks(self):
        with self.conn as conn:
            conn.execute(_SQLStatements.flush_checks)

class InstanceCheck(object):
    """
    """
    def __init__(self, check_id, check_type, check_params, delay, offset, jitter):
        """
        :type check_id: cifparser.Path
        :type check_type: str
        :type check_params: cifparser.Namespace
        :type delay: float
        :type offset: float
        :type jitter: float
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

    create_v1_manifest_url_table = """
CREATE TABLE IF NOT EXISTS v1_manifest_url ( manifest_url TEXT );
"""

    create_v1_endpoint_url_table = """
CREATE TABLE IF NOT EXISTS v1_endpoint_url ( endpoint_url TEXT );
"""

    create_v1_check_table = """
CREATE TABLE IF NOT EXISTS v1_check (
    check_id TEXT PRIMARY KEY,
    check_type TEXT,
    check_params TEXT,
    delay REAL,
    offset REAL,
    jitter REAL
);
"""

    create_v1_metadata_table = """
CREATE TABLE IF NOT EXISTS v1_metadata (
    name TEXT PRIMARY KEY,
    value TEXT
);
"""

    get_version = "SELECT version_number FROM version WHERE rowid=0;"

    set_version = "INSERT OR REPLACE INTO version ( rowid, version_number ) VALUES ( 0, ? );"

    get_agent_id = "SELECT agent_id from v1_agent_id WHERE rowid=0;"

    set_agent_id = "INSERT OR REPLACE INTO v1_agent_id ( rowid, agent_id ) VALUES ( 0, ? );"

    get_manifest_url = "SELECT manifest_url from v1_manifest_url WHERE rowid=0;"

    set_manifest_url = "INSERT OR REPLACE INTO v1_manifest_url ( rowid, manifest_url ) VALUES ( 0, ? );"

    get_endpoint_url = "SELECT endpoint_url from v1_endpoint_url WHERE rowid=0;"

    set_endpoint_url = "INSERT OR REPLACE INTO v1_endpoint_url ( rowid, endpoint_url ) VALUES ( 0, ? );"

    list_metadata = "SELECT name, value FROM v1_metadata;"

    get_meta_value = "SELECT value FROM v1_metadata WHERE name=?;"

    set_meta_value = "INSERT OR REPLACE INTO v1_metadata (name, value) VALUES ( ?, ?);"

    delete_meta_value = "DELETE FROM v1_metadata WHERE name=?;"

    flush_metadata = "DELETE FROM v1_metadata;"

    list_checks = "SELECT check_id, check_type, check_params, delay, offset, jitter FROM v1_check;"

    get_check = "SELECT check_id, check_type, check_params, delay, offset, jitter FROM v1_check WHERE check_id=?;"

    set_check = "INSERT OR REPLACE INTO v1_check (check_id, check_type, check_params, delay, offset, jitter) VALUES ( ?, ?, ?, ?, ?, ?);"

    delete_check = "DELETE FROM v1_check WHERE check_id=?;"

    flush_checks = "DELETE FROM v1_check;"

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
