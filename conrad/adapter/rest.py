import json
import logging
import restkit

from base import Base

logger = logging.getLogger(__name__)


class Rest(Base):

    def connect(self, uri):
        self.uri = uri
        self.resource = restkit.Resource(self.uri)

    def list(self, resource):
        return self.find(resource)

    def find(self, resource, conditions={}):
        logger.debug('Finding resource {} with conditions {}'.format(
                resource, conditions))
        if 'id' in conditions:
            res = self.resource.get('{}/{}'.format(resource, conditions['id']))
        else:
            res = self.resource.get(resource, params_dict=conditions)
        logger.debug('Find will convert {} to a result dict'.format(res))
        return [self.result_dict(res.body_string())]

    def delete(self, resource, conditions={}):
        if 'id' in conditions:
            res = self.resource.delete('{}/{}'.format(resource, conditions['id']))
        else:
            res = self.resource.delete(resource, params_dict=conditions)
        return self.result_dict(res.body_string())

    def update(self, resource, attributes={}, conditions={}):
        if 'id' in conditions:
            res = self.resource.put('{}/{}'.format(resource, conditions['id']), payload=attributes)
        else:
            res = self.resource.put(resource, params_dict=conditions, payload=attributes)
        return self.result_dict(res.body_string())

    def create(self, resource, attributes):
        logger.debug('Creating {} with attributes {}'.format(resource, attributes))
        res = self.resource.post(resource, payload=attributes)
        d = [self.result_dict(res.body_string())]
        logger.debug('Rest.create() is returning: {}'.format(d))
        return d

    def result_dict(self, result):
        logger.debug('Converting {} to dict'.format(result))
        return json.loads(result)
