from collections import defaultdict
from urllib.parse import urlparse, urljoin

from itemadapter import ItemAdapter
from itemloaders import ItemLoader
from itemloaders.processors import Compose, Join, TakeFirst
from itemloaders.utils import arg_to_iter
from scrapy import Item, Field
from scrapy_app.utils import remove_spaces


class ToString:
    """Convert values to string"""
    def __call__(self, values):
        for v in values:
            yield str(v) if v is not None else ''


class RemoveSpaces:
    """Convert values to strings without spaces"""
    def __call__(self, values):
        for v in values:
            yield remove_spaces(v)


class ToLowerCase:
    """Convert values to lower case"""
    def __call__(self, values):
        for v in values:
            yield v.lower()


class ToFloat:
    """Convert values to float"""
    def __call__(self, values):
        for v in values:
            if v not in [None, '']:
                yield float(str(v))


class ToAbsoluteUrl:
    """Convert relative urls to absolute using response.urljoin"""
    def __call__(self, values, loader_context=None):
        response = loader_context.get('response')
        for v in values:
            yield response.urljoin(v)


class RemoveQueryStringFromUrl:
    def __call__(self, values):
        for v in values:
            yield urljoin(v, urlparse(v).path)


class ToList:
    """Convert values to list"""
    def __call__(self, values):
        return [v for v in values]


class MakeUnique:
    """Remove duplicated values from list"""
    def __call__(self, values):
        return list(set(values))


# default combinations of output processors
string_cell = Compose(ToString(), RemoveSpaces(), TakeFirst())
list_cell = Compose(ToString(), RemoveSpaces(), MakeUnique(), Join(' | '))


class DynamicItem(Item):
    """
    Dynamic item - doesn't require specifying fields
    """
    fields = defaultdict(Field)


class DynamicItemLoader(ItemLoader):
    """
    Dynamic item loader - doesn't require specifying fields and process values as string by default
    """
    default_item_class = DynamicItem
    default_output_processor = string_cell

    def get_value(self, value, *processors, **kw):
        if value is None:  # custom code to avoid discarding None values
            value = []
        value = super().get_value(value, *processors, **kw)
        return value

    def _add_value(self, field_name, value):
        value = arg_to_iter(value)
        processed_value = self._process_input_value(field_name, value)
        self._values.setdefault(field_name, [])     # custom code to avoid discarding None values
        self._values[field_name] += arg_to_iter(processed_value)

    def load_item(self):
        adapter = ItemAdapter(self.item)
        for field_name in tuple(self._values):
            value = self.get_output_value(field_name)
            adapter[field_name] = value             # custom code to avoid discarding None values
        return adapter.item
