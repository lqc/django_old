from django.test import TestCase, RequestFactory
from django.utils import unittest
from django.utils.decorators import method_decorator, wraps, view_decorator

class DecoratorFromMiddlewareTests(TestCase):
    """
    Tests for view decorators created using
    ``django.utils.decorators.decorator_from_middleware``.
    """

    def test_process_view_middleware(self):
        """
        Test a middleware that implements process_view.
        """
        self.client.get('/utils/xview/')

    def test_callable_process_view_middleware(self):
        """
        Test a middleware that implements process_view, operating on a callable class.
        """
        self.client.get('/utils/class_xview/')


# For testing method_decorator, a decorator that assumes a single argument.
# We will get type arguments if there is a mismatch in the number of arguments.
def simple_dec(func):
    def wrapper(request, arg):
        return func(request, "test:" + arg)
    wrapper = wraps(func)(wrapper)
    wrapper.is_decorated = True
    return wrapper

simple_dec_m = method_decorator(simple_dec)


class MethodDecoratorTests(TestCase):
    """
    Tests for method_decorator.
    """
    
    @unittest.expectedFailure
    def test_method_decorator(self):
        class Test(object):
            @simple_dec_m
            def say(self, request, arg):
                return arg

        self.assertEqual("test:hello", Test().say(None, "hello"))
        self.assertTrue(getattr(Test().say, "is_decorated", False),
                "Method decorator didn't preserve attributes.")


class ClassBasedViewDecorationTests(TestCase):
    rf = RequestFactory() 
    
    def test_decorate_dispatch(self):
        from django.views.generic import View
                
        class MyView(View):
            
            def get(self, request, text):
                return "get:" + text
            
            def post(self, request, text):
                return "post:" + text
        MyView = view_decorator(simple_dec)(MyView)
        
        self.assertTrue(getattr(MyView.as_view(), "is_decorated", False),
                    "Class based view decorator didn't preserve attributes.")
        self.assertEqual(MyView.as_view()(self.rf.get('/'), "hello"), "get:test:hello")
        self.assertEqual(MyView.as_view()(self.rf.post('/'), "hello"), "post:test:hello")