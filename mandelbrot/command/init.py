import pathlib
import datetime
import logging
import cifparser

from mandelbrot.instance import create_instance, InstanceCheck
from mandelbrot.log import utility_format

def init_main(ns):
    """
    """
    if ns.verbose == True:
        logging.basicConfig(level=logging.DEBUG, format=utility_format)
    else:
        logging.basicConfig(level=logging.INFO, format=utility_format)
    log = logging.getLogger('mandelbrot')

    agent_id = ns.agent_id
    manifest_path = ns.manifest_path
    endpoint_url = ns.endpoint_url
    default_interval = datetime.timedelta(seconds=60)
    default_offset = datetime.timedelta(seconds=0)
    default_jitter = datetime.timedelta(seconds=0)

    # determine the manifest url
    manifest_path = pathlib.Path(manifest_path).absolute()
    manifest_url = manifest_path.as_uri()
    f = manifest_path.open('r')
    log.debug("reading manifest from %s", manifest_path.as_posix())

    # read manifest
    with f:
        values = cifparser.parse_file(f)

    # parse manifest
    metadata = values.get_container_fields(cifparser.make_path('metadata'))
    instance_checks = []

    def load_checks(path, parent):
        for name,container in parent.get_container_containers(cifparser.ROOT_PATH).items():
            check_id = cifparser.make_path(path, name)
            if container.contains_field(cifparser.ROOT_PATH, 'type'):
                check_fields = container.get_container_fields(cifparser.ROOT_PATH)
                check_params = cifparser.Namespace(cifparser.load(check_fields))
                check_type = check_params.get_flattened(cifparser.ROOT_PATH, 'type')
                check_fields.pop('type', None)
                interval = check_params.get_timedelta_or_default(cifparser.ROOT_PATH,
                    'interval', default_interval).total_seconds()
                check_fields.pop('interval', None)
                offset = check_params.get_timedelta_or_default(cifparser.ROOT_PATH,
                    'offset', default_jitter).total_seconds()
                check_fields.pop('offset', None)
                jitter = check_params.get_timedelta_or_default(cifparser.ROOT_PATH,
                    'jitter', default_offset).total_seconds()
                check_fields.pop('jitter', None)
                check_params = cifparser.Namespace(cifparser.load(check_fields))
                instance_check = InstanceCheck(check_id, check_type, check_params, interval, offset, jitter)
                instance_checks.append(instance_check)
                log.debug("loaded check %s", check_id)
            load_checks(check_id, container)

    load_checks(cifparser.ROOT_PATH, values.get_container(cifparser.make_path('checks')))

    # create instance
    instance = create_instance(pathlib.Path(ns.path))
    with instance.lock():
        instance.set_agent_id(agent_id)
        log.debug("set agent id => %s", agent_id)
        instance.set_manifest_url(manifest_url)
        log.debug("set manifest url => %s", manifest_url)
        instance.set_endpoint_url(endpoint_url)
        log.debug("set endpoint url => %s", endpoint_url)
        for meta_name,meta_value in metadata.items():
            instance.set_meta_value(meta_name, meta_value)
            log.debug("set meta value => %s", (meta_name,meta_value))
        for instance_check in instance_checks:
            instance.set_check(instance_check)
            log.debug("set check %s", instance_check.check_id)

    return 0
