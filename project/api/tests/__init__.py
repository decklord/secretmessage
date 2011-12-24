def get_test_modules():
    from os import path, listdir

    names = set()
    for f in listdir(path.dirname(__file__)):
        if f.startswith('.') or f.startswith('__'):
            continue
        names.add(f.split('.')[0])

    for name in names:
        yield (name, __import__('%s.%s' % (__name__, name), {}, {}, ['']))

def setup_doc_tests():
    for name, module in get_test_modules():
        # Try to find an API test in the current module, if it fails continue.
        try:
            api_tests = module.__test__['API_TESTS']
        except (AttributeError, TypeError, KeyError):
            continue

        # Import possible dependecies of the API test from the current module.
        for k, v in module.__dict__.iteritems():
            if k.startswith('__'):
                continue
            globals()[k] = v

        # Attach the API test to the __test__ dictionary if it exists or create it.
        try:
            globals()['__test__'][name] = api_tests
        except KeyError:
            globals()['__test__'] = {name: api_tests}

def setup_unit_tests():
    import unittest

    for name, module in get_test_modules():
        # Import each TestCase from the current module.
        for k, v in module.__dict__.iteritems():
            if not (isinstance(v, type) and issubclass(v, unittest.TestCase)):
                continue
            globals()[k] = v

setup_doc_tests()
setup_unit_tests() 
