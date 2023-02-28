import logging
log = logging.getLogger(__name__)

from pyramid.view import view_config, view_defaults

@view_defaults(renderer='home.jinja2')
class TutorialViews:
    def __init__(self, request):
        self.request = request

    # /h
    @view_config(route_name='h')
    def home(self):
        log.debug('In home view')
        return {'name': 'Home View'}

    # /howdy.json and /howdy
    @view_config(route_name='hello')
    @view_config(route_name='hello_json', renderer='json')
    def hello(self):
        log.debug('In hello view')
        return {'name': 'Hello View'}


@view_defaults(route_name='hello2')
class TutorialViews2:
    def __init__(self, request):
        self.request = request
        self.view_name = 'TutorialViews'

    @property
    def full_name(self):
        first = self.request.matchdict['first']
        last = self.request.matchdict['last']
        return first + ' ' + last

    @view_config(route_name='home2', renderer='home2.jinja2')
    def home(self):
        return {'page_title': 'Home View'}

    # Retrieving /howdy/first/last the first time
    @view_config(renderer='hello.jinja2')
    def hello(self):
        return {'page_title': 'Hello View'}

    # Posting to /howdy/first/last via the "Edit" submit button
    @view_config(request_method='POST', renderer='edit.jinja2')
    def edit(self):
        new_name = self.request.params['new_name']
        return {'page_title': 'Edit View', 'new_name': new_name}

    # Posting to /howdy/first/last via the "Delete" submit button
    @view_config(request_method='POST', request_param='form.delete',
                 renderer='delete.jinja2')
    def delete(self):
        print ('Deleted')
        return {'page_title': 'Delete View'}