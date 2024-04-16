import os
from elasticsearch import Elasticsearch


class ElasticsearchDb:
    def __new__(cls, host, port, protocol="https", ca_certs=None, username=None, password=None):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ElasticsearchDb, cls).__new__(cls)

        return cls.instance

    def __init__(self, host, port, protocol="https", ca_certs=None, username=None, password=None):
        if protocol is None:
            raise Exception("Protocol cannot be None.")

        if host is None:
            raise Exception ("Host cannot be None.")
        
        if port is None:
            raise Exception("Port cannot be None.")
        
        protocol = protocol.lower()

        if protocol not in ["http", "https"]:
            raise Exception("Invalid protocol: it must be http or https.")

        kwargs = {}

        if username is not None and password is not None:
            kwargs["basic_auth"] = (username, password)

        if ca_certs is not None:
            kwargs["ca_certs"] = ca_certs
        
        self.__es = Elasticsearch(str(protocol) + "://" + str(host) + ":" + str(port), **kwargs)

    
    @property
    def elasticsearch(self) -> Elasticsearch:
        return self.__es