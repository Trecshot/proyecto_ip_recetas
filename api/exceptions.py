from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        detail = response.data.get("detail", response.data) if isinstance(response.data, dict) else response.data
        response.data = {"error": {"status": response.status_code, "detail": detail}}
    return response
