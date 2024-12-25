from flask import jsonify, make_response

def create_response(data=None, message="", status=200, headers=None):
    """
    Creates a standardized Flask Response object.
    
    Args:
        data (any): Data to include in the response body.
        message (str): Message describing the response.
        status (int): HTTP status code.
        headers (dict): Additional headers to include.
    
    Returns:
        Response: Flask Response object.
    """
    response_body = {
        "data": data,
        "message": message,
        "status": status
    }
    response = make_response(jsonify(response_body), status)
    if headers:
        for key, value in headers.items():
            response.headers[key] = value
    return response
