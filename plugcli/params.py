import click


def _decorator_not_implemented(*args, **kwargs):
    raise NotImplementedError("'decorator' is not implemented for this "
                              "class")


class AbstractParameter:
    """
    Abstract wrapper for click parameters.

    Parameters
    ----------
    args :
        Arguments to pass to click parameter
    getter : Callable
        function to create desired object from user input and context dict;
        default behavior is to return user input; keyword-only
    kwargs :
        Keyword arguments to pass to click parameter
    """
    decorator = _decorator_not_implemented
    def __init__(self, *args, getter=None, **kwargs):
        self.args = args
        self.kwargs = kwargs
        if getter is None:
            getter = lambda user_input, context: user_input
        self.getter = getter

    def parameter(self, **kwargs):
        """Return the click decorator for this parameter

        Parameters
        ----------
        kwargs :
            additional click parameters; overrides anything set in
            initialization

        Returns
        Callable :
            the click decorator to use in a command
        """
        # kwargs given here override those given on initialization

        decorator_kwargs = self.kwargs.copy()
        decorator_kwargs.update(kwargs)
        dec = self.__class__.decorator(*self.args, **decorator_kwargs)
        return dec

    def get(self, user_input, context=None):
        """Convert user input to library object using provided getter

        Parameters
        ----------
        user_input :
            input as handled by click decorators
        context : Dict[str, Any]
            dict mapping labels to other objects that may be used by this.
        """
        return self.getter(user_input, context)


class Option(AbstractParameter):
    """Wrapper for click.option decorators"""
    decorator = click.option


class Argument(AbstractParameter):
    """Wrapper for click.argument decorators"""
    decorator = click.argument


NOT_PARSED = object()


class MultiStrategyGetter:
    """
    Callable that combines attempts multiple strategies to parse user input.

    Parameters
    ----------
    strategies : List[Callable[str, Dict[str, Any], Any]]
        list of callables, each representing one strategy for creating the
        desired object from the user input.
    error_message : str
        message to provide if no object found; ``.format`` will be used to
        expand ``user_input``
    """
    def __init__(self, strategies, error_message):
        self.strategies = strategies
        self.error_message = error_message

    def __call__(self, user_input, context=None):
        """
        Parameters
        ----------
        user_input :
            parameter as handled by click decorators
        context : Dict
            mapping of str to additional information available to help
            create this object
        """
        if context is None:
            context = {}

        for strategy in self.strategies:
            found = strategy(user_input, context)
            if found is not NOT_PARSED:
                return found

        raise click.BadParameter(
            self.error_message.format(user_input=user_input)
        )
