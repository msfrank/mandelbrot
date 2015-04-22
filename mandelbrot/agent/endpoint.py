import asyncio
import requests
import logging

log = logging.getLogger("mandelbrot.agent.endpoint")

import mandelbrot.endpoint

class Endpoint(mandelbrot.endpoint.Endpoint):
    """
    """

    def get_agent(self, agent_id):
        """
        :param agent_id:
        :type agent_id: str
        :returns: The ResponseItem object wrapped in a Future.
        :rtype: asyncio.Future[ResponseItem]
        """
        request = requests.Request(method='GET',
            url=self.absolute_url('v2/systems/' + agent_id)
            )
        return self.request_response(request)

    def register_agent(self, agent_id, registration):
        """
        :param agent_id:
        :type agent_id: str
        :returns: The ResponseItem object wrapped in a Future.
        :rtype: asyncio.Future[ResponseItem]
        """
        request = requests.Request(method='POST', url=self.absolute_url('v2/systems'),
            json=registration.destructure())
        return self.request_response(request)

    def update_agent(self, agent_id, registration):
        """
        :param agent_id:
        :type agent_id: str
        :returns: The ResponseItem object wrapped in a Future.
        :rtype: asyncio.Future[ResponseItem]
        """
        request = requests.Request(method='PUT',
            url=self.absolute_url('v2/systems/' + agent_id),
            json=registration.destructure())
        return self.request_response(request)

    def unregister_agent(self, agent_id):
        """
        :param agent_id:
        :type agent_id: str
        :returns: The ResponseItem object wrapped in a Future.
        :rtype: asyncio.Future[ResponseItem]
        """
        request = requests.Request(method='DELETE',
            url=self.absolute_url('v2/systems/' + agent_id),
            )
        return self.request_response(request)

    def submit_evaluation(self, agent_id, check_id, evaluation):
        """
        """
        request = requests.Request(method='POST',
            url=self.absolute_url('v2/systems/' + agent_id + '/probes/' + check_id),
            json=evaluation.destructure())
        return self.request_response(request)
