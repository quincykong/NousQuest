from flask import request

def get_pagination_params():
    """
    Extracts pagination parameters from the request query string.
    
    Returns:
        dict: Pagination parameters with defaults.
    """
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    return {"page": page, "per_page": per_page}
