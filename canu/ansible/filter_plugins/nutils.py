from netutils.utils import jinja2_convenience_function


class FilterModule(object):
    def filters(self):
        return jinja2_convenience_function()
