from pyramid.response import Response
from pyramid.security import Allow, Authenticated, DENY_ALL
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from ..models import DBSession, User, Roles


class RouteContext(object):
    __acl__ = [ (Allow, Authenticated, Roles.USERS), DENY_ALL ]
    
    def __init__(self, request):
        pass


# @view_config(route_name='home', renderer='../templates/mytemplate.pt',
#              permission=Roles.USERS)
# def my_view(request):
#     try:
#         DBSession.query(User).all()
#     except DBAPIError:
#         return Response(conn_err_msg, content_type='text/plain', status_int=500)
#     return {'project': 'Unsonic'}


# conn_err_msg = """\
# Unsonic is having a problem using your SQL database.  The problem
# might be caused by one of the following things:

# 1.  You may need to run the "unsonic-db init" script
#     to initialize your database tables.

# 2.  Your database server may not be running.  Check that the
#     database server referred to by the "sqlalchemy.url" setting in
#     your "development.ini" file is running.

# After you fix the problem, please restart Unsonic to try it again.
# """

