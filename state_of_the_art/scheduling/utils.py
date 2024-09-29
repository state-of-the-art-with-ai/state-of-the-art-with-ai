from functools import wraps


def capture_exeption():
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

            print(f"Function {func.__name__} ended")
            return result

        return __

    return _
