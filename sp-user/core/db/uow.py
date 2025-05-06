class UOW:
    def __init__(self, session):
        self.session = session

    def begin(self):
        self.session.begin()

    async def rollback(self):
        await self.session.rollback()

    async def commit(self):
        await self.session.commit()

    async def __aenter__(self):
        self.begin()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.rollback()
        await self.session.close()


def get_uow(session):
    return UOW(session)
