import pytest

from plugcli.params import *


class ParameterTest:
    plugcli_class = None
    def setup_method(self):
        if self.plugcli_class is Option:
            self.name = "--foo"
        elif self.plugcli_class is Argument:
            self.name = "foo"
        else:  # -no-cov-
            raise RuntimeError(f"Invalid class for testing: "
                               "'{self.plugcli_class.__class__.__name__}'")

        self.param = self.plugcli_class(
            self.name, required=True, type=int,
            getter=lambda user_input, context: user_input + 1
        )

    def test_get(self):
        # the parameter as loaded by click should already be an int, this
        # converts uses the getter method on it (which adds 1 in this
        # example)
        assert self.param.get(1, {}) == 2

    def test_default_get(self):
        param = self.plugcli_class(
            self.name, required=True, type=int
        )
        assert param.get(3) == 3

    @pytest.mark.parametrize('override', [
        {},
        {'required': False}
    ])
    def test_parameter(self, override):
        expected = {'required': True}
        expected.update(override)

        def f(foo): pass
        p1 = self.param.parameter(**override)
        p1f = p1(f)  # f after decorating with the parameter

        assert len(p1f.__click_params__) == 1
        param = p1f.__click_params__[0]
        assert isinstance(param, self.click_class)
        assert param.name == "foo"
        assert param.required is expected['required']
        assert isinstance(param.type, click.types.IntParamType)


class TestOption(ParameterTest):
    plugcli_class = Option
    click_class = click.Option


class TestArgument(ParameterTest):
    plugcli_class = Argument
    click_class = click.Argument


class TestMultiStrategyGetter:
    def setup_method(self):
        self.pass_strategy = lambda user_input, context: str(user_input)
        self.fail_strategy = lambda user_input, context: NOT_PARSED
        self.error_message = "bad input '{user_input}'"
        self.expected_error = "bad input '3'"

    def test_fail(self):
        getter = MultiStrategyGetter([self.fail_strategy],
                                     self.error_message)
        with pytest.raises(click.BadParameter, match=self.expected_error):
            x = getter(3)

    def test_pass_then_fail(self):
        getter = MultiStrategyGetter(
            strategies=[self.pass_strategy, self.fail_strategy],
            error_message=self.error_message
        )
        assert getter(3) == "3"

    def test_fail_then_pass(self):
        getter = MultiStrategyGetter(
            strategies=[self.fail_strategy, self.pass_strategy],
            error_message=self.error_message
        )
        assert getter(3) == "3"

    def test_pass(self):
        getter = MultiStrategyGetter(
            strategies=[self.pass_strategy],
            error_message=self.error_message
        )
        assert getter(3) == "3"
