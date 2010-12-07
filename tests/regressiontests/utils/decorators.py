from django.test import TestCase, RequestFactory
from django.utils import unittest
from django.utils.decorators import method_decorator, wraps, view_decorator
from django.views.generic import View


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


def simple_dec(func):
    """
    Simple decotator for testing method_decorator and view_decorator.
    It assumes a request argument and one extra argument.  Appends
    string "decorator:" to the result. It also sets `is_decorated` attribute
    on the wrappper.
    """
    def wrapper(request, arg):
        return "decorator:" + func(request, arg)
    wrapper = wraps(func)(wrapper)
    wrapper.is_decorated = True
    return wrapper


def dec_with_arg(decarg):
    def decorator(view):
        @wraps(view)
        def wrapped(request, arg):
            return "dec(%s):%s" % (decarg, view(request, arg))
        return wrapped
    decorator.__name__ = "Decorator(%s)" % decarg
    return decorator


class MethodDecoratorTests(TestCase):
    """
    Tests for method_decorator.
    """

    def test_method_decorator(self):
        simple_dec_m = method_decorator(simple_dec)

        class Test(object):
            @simple_dec_m
            def say(self, request, arg):
                return arg

        self.assertEqual("decorator:hello", Test().say(None, "hello"))
        self.assertTrue(getattr(Test().say, "is_decorated", False),
                "Method decorator didn't preserve attributes.")


class ClassBasedViewDecorationTests(TestCase):
    rf = RequestFactory()

    def test_decorate_view(self):
        class TextView(View):
            "Docstring"
            def get(self, request, text):
                return "get:" + text
            def post(self, request, text):
                return "post:" + text
        TextView = view_decorator(simple_dec)(TextView)

        self.assertTrue(getattr(TextView.as_view(), "is_decorated", False),
                    "Class based view decorator didn't preserve attributes.")
        self.assertEqual(TextView.as_view().__doc__, "Docstring",
                    "Class based view decorator didn't preserve docstring.")
        self.assertEqual(TextView.as_view()(self.rf.get('/'), "hello"), "decorator:get:hello")
        self.assertEqual(TextView.as_view()(self.rf.post('/'), "hello"), "decorator:post:hello")

    def test_multiply_decorators(self):
        class TextView(View):
            def dispatch(self, request, text):
                return "view:" + text

        TextView = view_decorator(dec_with_arg("bottom"))(TextView)
        TextView = view_decorator(dec_with_arg("top"))(TextView)
        v = TextView.as_view()       
        self.assertEqual(v(self.rf.get('/'), "hello"), "dec(top):dec(bottom):view:hello")

    def test_super_calls(self):
        class TextView(View):
            def dispatch(self, request, text):
                return "view1:" + text

        # NOTE: it's important for this test, that the definition
        # and decoration of the class happens in the *same scope*.
        class ViewWithSuper(TextView):

            def __init__(self, **initargs):
                self.recursion_count = 0
                super(ViewWithSuper, self).__init__(**initargs)

            def dispatch(self, *args, **kwargs):
                self.recursion_count += 1
                if self.recursion_count > 10:
                    raise Exception("Decoration caused recursive super() calls.")
                return "view2:" + super(ViewWithSuper, self).dispatch(*args, **kwargs)
        ViewWithSuper = view_decorator(simple_dec)(ViewWithSuper)

        self.assertEqual(ViewWithSuper.as_view()(self.rf.get('/'), "A"), "decorator:view2:view1:A")

    @unittest.expectedFailure
    def test_super_calls_with_subclassing(self):
        class TextView(View):
            def dispatch(self, request, text):
                return "view1:" + text

        # NOTE: it's important for this test, that the definition
        # and decoration of the class happens in the *same scope*.
        class ViewWithSuper(TextView):

            def __init__(self, **initargs):
                self.recursion_count = 0
                super(ViewWithSuper, self).__init__(**initargs)

            def dispatch(self, *args, **kwargs):
                self.recursion_count += 1
                if self.recursion_count > 10:
                    raise RuntimeError("Decoration caused recursive super() calls.")
                return "view2:" + super(ViewWithSuper, self).dispatch(*args, **kwargs)
        ViewWithSuper = view_decorator(simple_dec, subclass=True)(ViewWithSuper)

        self.assertEqual(ViewWithSuper.as_view()(self.rf.get('/'), "A"), "decorator:view2:view1:A")

    def test_subclassing_decorated(self):
        """
        Test that decorators are always pushed to front.
        """
        class TextView(View):
            def dispatch(self, request, text):
                return "view1:" + text
        TextView = view_decorator(simple_dec)(TextView)

        class SubView(TextView):
            def dispatch(self, *args, **kwargs):
                return "view2:" + super(SubView, self).dispatch(*args, **kwargs)

        self.assertEqual(SubView.as_view()(self.rf.get('/'), "A"), "decorator:view2:view1:A")

    @unittest.expectedFailure
    def test_base_unmodified(self):
        class TextView(View):
            attr = "OK"
            def dispatch(self, request, text):
                return "view1:" + text
        DecoratedView = view_decorator(simple_dec)(TextView)
        self.assertEqual(DecoratedView.as_view()(self.rf.get('/'), "A"), "decorator:view1:A")
        self.assertEqual(TextView.as_view()(self.rf.get('/'), "A"), "view1:A")
        self.assertFalse(DecoratedView is TextView)
        self.assertEqual(DecoratedView.mro(), [DecoratedView, TextView, View, object])

    def test_base_unmodified_with_subclassing(self):
        class TextView(View):
            attr = "OK"
            def dispatch(self, request, text):
                return "view1:" + text
        DecoratedView = view_decorator(simple_dec, subclass=True)(TextView)

        self.assertEqual(DecoratedView.as_view()(self.rf.get('/'), "A"), "decorator:view1:A")
        self.assertEqual(TextView.as_view()(self.rf.get('/'), "A"), "view1:A")
        self.assertFalse(DecoratedView is TextView)
        self.assertEqual(DecoratedView.mro(), [DecoratedView, TextView, View, object])
