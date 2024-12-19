def create_response(data=None, message="", status=200):
    """
    Standardizes the structure of API responses.
    
    Args:
        data (any): The primary data payload (optional).
        message (str): A human-readable message describing the result (optional).
        status (int): HTTP status code or custom status indicator (default: 200).
    
    Returns:
        dict: A standardized response object.
    """
    return {
        "data": data,
        "message": message,
        "status": status
    }
