import datetime
import cifparser

from mandelbrot.model import StructuredMixin, add_constructor, construct

class AgentMetadata(StructuredMixin):
    """
    """
    def __init__(self):
        self.agent_id = None
        self.joined_on = None
        self.last_update = None
        self.lsn = None

    def get_agent_id(self):
        return self.agent_id

    def set_agent_id(self, agent_id):
        assert isinstance(agent_id, cifparser.Path)
        self.agent_id = agent_id

    def get_joined_on(self):
        return self.joined_on

    def set_joined_on(self, joined_on):
        assert isinstance(joined_on, datetime.datetime)
        self.joined_on = joined_on

    def get_last_update(self):
        return self.last_update

    def set_last_update(self, last_update):
        assert isinstance(last_update, datetime.datetime)
        self.last_update = last_update

    def get_lsn(self):
        return self.lsn

    def set_lsn(self, lsn):
        assert isinstance(lsn, int)
        self.lsn = lsn

    def destructure(self):
        structure = {}
        structure['agentId'] = str(self.agent_id)
        structure['joinedOn'] = self.joined_on.isoformat()
        structure['lastUpdate'] = self.last_update.isoformat()
        structure['lsn'] = self.lsn
        return structure

class AgentMetadataPage(StructuredMixin):
    """
    """
    def __init__(self):
        self.agent_metadata = {}
        self.last = None
        self.exhausted = None

    def get_agent_metadata(self, agent_id):
        return self.agent_metadata[agent_id]

    def list_agent_metadata(self):
        return self.agent_metadata.items()

    def set_agent_metadata(self, agent_id, agent_metadata):
        assert isinstance(agent_id, cifparser.Path)
        assert isinstance(agent_metadata, AgentMetadata)
        self.agent_metadata[agent_id] = agent_metadata

    def delete_agent_metadata(self, agent_id):
        del self.agent_metadata[agent_id]

    def get_last(self):
        return self.last

    def set_last(self, last):
        assert isinstance(last, str)
        self.last = last

    def get_exhausted(self):
        return self.exhausted

    def set_exhausted(self, exhausted):
        assert isinstance(exhausted, bool)
        self.exhausted = exhausted

def _construct_agent_metadata(structure):
    agent_metadata = AgentMetadata()
    agent_metadata.set_agent_id(cifparser.make_path(structure['agentId']))
    joined_on = datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=int(structure['joinedOn']))
    agent_metadata.set_joined_on(joined_on)
    last_update = datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=int(structure['lastUpdate']))
    agent_metadata.set_last_update(last_update)
    agent_metadata.set_lsn(structure['lsn'])
    return agent_metadata

add_constructor(AgentMetadata, _construct_agent_metadata)

def _construct_agent_metadata_page(structure):
    page = AgentMetadataPage()
    for name,value in structure['agents'].items():
        agent_id = cifparser.make_path(name)
        agent_metadata = construct(AgentMetadata, value)
        page.set_agent_metadata(agent_id, agent_metadata)
    if 'last' in structure:
        page.set_last(structure['last'])
    return page

add_constructor(AgentMetadataPage, _construct_agent_metadata_page)
