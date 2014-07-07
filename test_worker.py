from turp.base_worker import BaseWorker, RpcError

class TestWorker(BaseWorker):
    def __init__(self):
        # initialize base worker
        super(TestWorker, self).__init__()
        # our various queues will be based off this
        self.queue_name = 'test'

    # Contrived authenticate function
    def authenticate(self, username, password):
        if username == 'test' and password == '123':
            return True
        elif username == 'test_client' and password == '123':
            id = self.client.send_request('work:test', 'authenticate', 'invalid_test_client', 'invalid')
            return id
        else:
            raise RpcError(1234, "Invalid login")

if __name__ == '__main__':
    TestWorker().start()
