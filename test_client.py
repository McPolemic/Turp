from turp.client import Client

if __name__ == '__main__':
    client = Client()

    queue_name = 'work:test'

    id = client.send_request(queue_name, 'authenticate', 'incorrect', 'password')
    response = client.get_response(id)
    print 'First response: {}'.format(response)

    id = client.send_request(queue_name, 'authenticate', 'test', '123')
    response = client.get_response(id)
    print 'Second response: {}'.format(response)

    id = client.send_request(queue_name, 'authenticate', 'test_client', '123')
    response = client.get_response(id)
    print 'Third response: {}'.format(response)
