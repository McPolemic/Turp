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

    def current_request_id(self):
        return ','.join(self.request_id)

    def process_request(self, request):
        self.log_request(request)
        request_id = request['id']
        method = request['method']
        args = request['params']
        result = None
        error = None
        self.client = Client(self.redis, request_id)
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
        response = {'id': request_id,
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

        self.redis.rpush(request_id, json.dumps(response))
        self.redis.expire(request_id, 30)
        self.client = None
        print "Finished. Task ID is {}".format(request_id)

