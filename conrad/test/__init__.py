import os, os.path

resources_path = os.path.abspath(
                    os.path.join(
                        os.path.dirname(__file__),
                        'resources'))

def resource(name):
    """Returns the full path to a file under the test/resources
    directory."""
    path = os.path.join(resources_path, name)
    if not os.path.exists(path):
        raise OSError('Resource %s does not exist.' % name)
    return path

def resource_file(name):
    """Returns an open file object for the requested resource."""
    return open(resource(name))

def resource_contents(name):
    """Returns the contents of the requested resource."""
    return resource_file(name).read()