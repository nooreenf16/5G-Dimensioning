def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('h', '/h')
    config.add_route('hello', '/howdy')
    config.add_route('hello_json', '/howdy.json')
    config.add_route('hello2', '/hello2/{first}/{last}')
    config.add_route('home2', '/home2')
