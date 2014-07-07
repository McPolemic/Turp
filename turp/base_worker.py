import time
import simplejson as json
from redis import Redis
from client import Client

class RpcError(Exception):
    def __init__(self, number, message):
        self.number = number
        self.message = message

    def __str__(self):
        return self.message

class BaseWorker(object):
    def __init__(self, redis=Redis()):
        self.redis = redis
        self.client = Client(self.redis)

    def work_queue(self):
        return 'work:{}'.format(self.queue_name)

    def start(self):
        print "Running worker..."
        print "Monitoring {}".format(self.work_queue())
        while True:
            channel, request = self.redis.brpop(self.work_queue())
            request_data = json.loads(request)
            self.process_request(request_data)

    def log_request(self, request):
        print 'Received request {}'.format(request)

    def process_request(self, request):
        self.log_request(request)
        id = request['id']
        method = request['method']
        args = request['params']
        result = None
        error = None
        queue_end_time = time.time()*1000000

        try:
            if args:
                result = self.__getattribute__(method)(*args)
            else:
                result = self.__getattribute__(method)()
        except RpcError as e:
            error = {'code': e.number,
                     'message': e.message}

        work_end_time = time.time()*1000000
        response = {'id': id,
                    'jsonrpc': '2.0',
                    'queue_start_time': request['queue_start_time'],
                    'queue_end_time':   queue_end_time,
                    'work_end_time':    work_end_time}

        if error:
            print 'Got error {}'.format(error['message'])
            response['error'] = error
        else:
            print 'Got result {}'.format(result)
            response['result'] = result

        self.redis.rpush(id, json.dumps(response))
        self.redis.expire(id, 30)
        print "Finished. Task ID is {}".format(id)

