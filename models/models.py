import requests

# Microservice endpoints
service1_endpoint = 'http://localhost:5001/status'
service2_endpoint = 'http://localhost:5002/status'

def check_microservices():
    # Check status of microservices
    service1_status = 200#requests.get(service1_endpoint).status_code
    service2_status = 200#requests.get(service2_endpoint).status_code
    
    # Determine which microservice to use
    if service1_status == 200:
        return 'service1'
    elif service2_status == 200:
        return 'service2'
    else:
        return None
