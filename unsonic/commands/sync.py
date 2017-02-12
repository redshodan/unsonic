from mishmash.commands.sync import Sync

from ..models import initAlembic


org_run = Sync._run


def newrun(self, *args, **kwargs):
    ret = org_run(self, *args, **kwargs)
    if ret == 0 or ret is None:
        self.db_session.commit()
        initAlembic()
    return ret


Sync._run = newrun
