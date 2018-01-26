import re
import six
import types
import inspect


def describe(article, value, name=None, verbose=False, capital=False):
    """Return string that describes a value

    Parameters
    ----------
    article: str or None
        A definite or indefinite article. If the article is
        indefinite (i.e. "a" or "an") the appropriate one
        will be infered. Thus, the arguments of ``describe``
        can themselves represent what the resulting string
        will actually look like. If None, then no article
        will be prepended to the result. For non-articled
        description, values that are instances are treated
        definitely, while classes are handled indefinitely.
    value: any
        The value which will be named.
    name: str or None (default: None)
        Only applies when ``article`` is "the" - this
        ``name`` is a definite reference to the value.
        By default one will be infered from the value's
        type and repr methods.
    verbose: bool (default: False)
        Whether the name should be concise or verbose. When
        possible, verbose names include the module, and/or
        class name where an object was defined.
    capital: bool (default: False)
        Whether the first letter of the article should
        be capitalized or not. By default it is not.

    Examples
    --------

    Indefinite description:

    >>> describe("a", object())
    'an object'
    >>> describe("a", object)
    'an object'
    >>> describe("a", type(object))
    'a type'

    Definite description:

    >>> describe("the", object())
    "the object at '0x10741f1b0'"
    >>> describe("the", object)
    "the type 'object'"
    >>> describe("the", type(object))
    "the type 'type'"

    Definitely named description:

    >>> describe("the", object(), "I made")
    'the object I made'
    >>> describe("the", object, "I will use")
    'the object I will use'
    """
    if isinstance(article, str):
        article = article.lower()

    if not inspect.isclass(value):
        typename = type(value).__name__
    else:
        typename = value.__name__
    if verbose:
        typename = _prefix(value) + typename

    if article == "the" or (article is None and not inspect.isclass(value)):
        if name is not None:
            result = "%s %s" % (typename, name)
            if article is not None:
                final = add_article(result, True, capital)
            else:
                final = result.strip()
        else:
            tick_wrap = False
            if inspect.isclass(value):
                name = value.__name__
            elif isinstance(value, types.FunctionType):
                name = value.__name__
                tick_wrap = True
            elif isinstance(value, types.MethodType):
                name = value.__func__.__name__
                tick_wrap = True
            elif type(value).__repr__ in (object.__repr__, type.__repr__):
                name = "at '%s'" % hex(id(value))
                verbose = False
            else:
                name = repr(value)
                verbose = False
            if verbose:
                name = _prefix(value) + name
            if tick_wrap:
                name = name.join("''")
            final = describe(article, value, name=name,
                verbose=verbose, capital=capital)
    elif article in ("a", "an") or article is None:
        if article is None:
            final = typename
        else:
            final = add_article(typename, False, capital)
    else:
        raise ValueError("The 'article' argument should "
            "be 'the', 'a', 'an', or None not %r" % article)
    return final.strip()


def _prefix(value):
    if isinstance(value, types.MethodType):
        name = describe(None, value.__self__, verbose=True) + '.'
    else:
        module = inspect.getmodule(value)
        if module is not None and module.__name__ != "builtins":
            name = module.__name__ + '.'
        else:
            name = ""
    return name


def class_of(value):
    """Returns a string of the value's type with an indefinite article.

    For example 'an Image' or 'a PlotValue'.
    """
    if inspect.isclass(value):
        return add_article(value.__name__)
    else:
        return class_of(type(value))


def add_article(name, definite=False, capital=False):
    """Returns the string with a prepended article.

    The input does not need to begin with a charater.

    Parameters
    ----------
    definite: bool (default: False)
        Whether the article is definite or not.
        Indefinite articles being 'a' and 'an',
        while 'the' is definite.
    capital: bool (default: False)
        Whether the added article should have
        its first letter capitalized or not.
    """
    if definite:
        result = "the " + name
    else:
        first_letters = re.compile(r'[\W_]+').sub('', name)
        if first_letters[:1].lower() in 'aeiou':
            result = 'an ' + name
        else:
            result = 'a ' + name
    if capital:
        return result[0].upper() + result[1:]
    else:
        return result
    return result


def repr_type(obj):
    """Return a string representation of a value and its type for readable

    error messages.
    """
    the_type = type(obj)
    if six.PY2 and the_type is types.InstanceType:
        # Old-style class.
        the_type = obj.__class__
    msg = '%r %r' % (obj, the_type)
    return msg
