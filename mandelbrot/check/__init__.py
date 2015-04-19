import cifparser

class Check(object):
    """
    """
    def __init__(self, ns):
        """

        :param ns:
        :type ns: cifparser.Namespace
        :return:
        """
        self.ns = ns

    def get_join_timeout(self):
        return self.ns.get_timedelta(cifparser.ROOT_PATH, "join timeout")

    def get_probe_timeout(self):
        return self.ns.get_timedelta(cifparser.ROOT_PATH, "probe timeout")

    def get_alert_timeout(self):
        return self.ns.get_timedelta(cifparser.ROOT_PATH, "alert timeout")

    def get_retirement_age(self):
        return self.ns.get_timedelta(cifparser.ROOT_PATH, "retirement age")

    def get_allowed_notifications(self):
        return self.ns.get_str_list_or_default(cifparser.ROOT_PATH, "allowed notifications")

    def init(self):
        """
        Perform any initialization necessary before calling execute for the first time.
        """
        pass

    def fini(self):
        """
        Perform cleanup tasks before shutdown.
        """
        pass

    def get_behavior_type(self):
        """
        Return the server-side behavior.

        :rtype: str
        """
        raise NotImplementedError()

    def get_behavior(self):
        """

        :rtype: dict[str,str]
        """
        raise NotImplementedError()

    def execute(self):
        """
        Execute the check, and return an Evaluation.

        :rtype: mandelbrot.model.Evaluation
        """
        raise NotImplementedError()

    def __call__(self, *args, **kwargs):
        return self.execute()
