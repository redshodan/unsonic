from . import RestTestCase
from ...models import Session, User
from ...views.rest.createuser import CreateUser


class TestCreateUser(RestTestCase):
    def testCreateUser(self):
        cmd = self.buildCmd(CreateUser,
                            {"username": "test2", "password": "test2"}, "admin")
        self.checkResp(cmd.req, cmd())
        with Session() as session:
            row = session.query(User).filter(User.name == "test2").one_or_none()
            self.assertEqual(row.password, "test2")
