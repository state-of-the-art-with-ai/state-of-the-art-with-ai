from functools import wraps
from sentry_sdk import capture_exception



def capture_errors():
    def _(func):
        @wraps(func)
        def __(*args, **kwargs):
            result = None
            try:
                print(f"Function {func.__name__} started execution")
                result = func(*args, **kwargs)
            except Exception as e:
                print(
                    f"\nException {str(e)} in function  {func.__name__} but not failing the application\n\n"
                )
                capture_exception(e)

            print(f"Function {func.__name__} ended")
            return result

        return __

    return _
