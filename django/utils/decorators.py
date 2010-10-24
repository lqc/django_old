"Functions that help with dynamically creating decorators for views."

import types
try:
    from functools import wraps, update_wrapper, WRAPPER_ASSIGNMENTS
except ImportError:
    from django.utils.functional import wraps, update_wrapper, WRAPPER_ASSIGNMENTS  # Python 2.4 fallback.


def method_decorator(decorator):
    """
    Converts a function decorator into a method decorator
    """
    # 'func' is a function at the time it is passed to _dec, but will eventually
    # be a method of the class it is defined it.
    def _dec(func):
        def _wrapper(self, *args, **kwargs):
            @decorator
            def bound_func(*args2, **kwargs2):
                return func(self, *args2, **kwargs2)
            # bound_func has the signature that 'decorator' expects i.e.  no
            # 'self' argument, but it is a closure over self so it can call
            # 'func' correctly.
            return bound_func(*args, **kwargs)
        # In case 'decorator' adds attributes to the function it decorates, we
        # want to copy those. We don't have access to bound_func in this scope,
        # but we can cheat by using it on a dummy function.
        @decorator
        def dummy(*args, **kwargs):
            pass
        update_wrapper(_wrapper, dummy)
        # Need to preserve any existing attributes of 'func', including the name.
        update_wrapper(_wrapper, func)

        return _wrapper
    update_wrapper(_dec, decorator)
    # Change the name to aid debugging.
    _dec.__name__ = 'method_decorator(%s)' % decorator.__name__
    return _dec

def class_decorator(decorator):
    """
    Converts a function decorator into a class decorator suitable for Django's
    class based views implementation::

        @class_decorator(login_required):
        class ProtectedView(View):
            pass

    """
    def _dec(cls):
        decorated = method_decorator(decorator)(cls.dispatch)
        cls.dispatch = decorated
        return cls
    update_wrapper(_dec, decorator)
    # Change the name to aid debugging.
    _dec.__name__ = 'class_decorator(%s)' % (decorator.__name__)
    return _dec


def view_decorator(fdec):
    """
    Change a function decorator into a view decorator.

    This is a simplest approach possible. as_view() is overriden, so
     that is applies the given decorator before returning.

    In this approach, decorators are always put on top - that means it's not
    possible to have functions called in this order:

       B.dispatch, login_required, A.dispatch

    """
    from django.views.generic.base import classonlymethod
    def decorator(cls):
        def as_view(current, **initkwargs):
            return fdec(super(cls, current).as_view(**initkwargs))
        cls.as_view = classonlymethod(as_view)
        return cls
    return decorator


def decorator_from_middleware_with_args(middleware_class):
    """
    Like decorator_from_middleware, but returns a function
    that accepts the arguments to be passed to the middleware_class.
    Use like::

         cache_page = decorator_from_middleware_with_args(CacheMiddleware)
         # ...

         @cache_page(3600)
         def my_view(request):
             # ...
    """
    return make_middleware_decorator(middleware_class)


def decorator_from_middleware(middleware_class):
    """
    Given a middleware class (not an instance), returns a view decorator. This
    lets you use middleware functionality on a per-view basis. The middleware
    is created with no params passed.
    """
    return make_middleware_decorator(middleware_class)()


def available_attrs(fn):
    """
    Return the list of functools-wrappable attributes on a callable.
    This is required as a workaround for http://bugs.python.org/issue3445.
    """
    return tuple(a for a in WRAPPER_ASSIGNMENTS if hasattr(fn, a))


def make_middleware_decorator(middleware_class):
    def _make_decorator(*m_args, **m_kwargs):
        middleware = middleware_class(*m_args, **m_kwargs)
        def _decorator(view_func):
            def _wrapped_view(request, *args, **kwargs):
                if hasattr(middleware, 'process_request'):
                    result = middleware.process_request(request)
                    if result is not None:
                        return result
                if hasattr(middleware, 'process_view'):
                    result = middleware.process_view(request, view_func, args, kwargs)
                    if result is not None:
                        return result
                try:
                    response = view_func(request, *args, **kwargs)
                except Exception, e:
                    if hasattr(middleware, 'process_exception'):
                        result = middleware.process_exception(request, e)
                        if result is not None:
                            return result
                    raise
                if hasattr(middleware, 'process_response'):
                    result = middleware.process_response(request, response)
                    if result is not None:
                        return result
                return response
            return wraps(view_func, assigned=available_attrs(view_func))(_wrapped_view)
        return _decorator
    return _make_decorator
