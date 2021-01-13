# -*- coding: utf-8 -*-
# Sortable dict helper class
# Use license Apache V2.0
# (C) 2016 VRT Systems
# (C) 2021 Engie Digital
#
# vim: set ts=4 sts=4 et tw=78 sw=4 si:

"""
A sortable dictionary
"""
import collections.abc as col
import copy
import sys
from typing import Callable, Any, Optional, Dict, Iterator, Union, List, Tuple

import six


class SortableDict(col.MutableMapping):
    """
    A dict-like object that permits value ordering/re-ordering.
    """

    def __init__(self,
                 initial: Union[None, List[Tuple[str, Any]], Dict[str, Any]] = None,
                 validate_fn: Optional[Callable[[Any], bool]] = None):
        self._values = {}
        self._order = []
        self._validate_fn = validate_fn
        super().__init__()

        # Copy initial values into dict.
        if initial is not None:
            # If we're given a dict; make it a list of items
            if isinstance(initial, dict):
                initial = list(initial.items())

            for (key, val) in initial:
                self[key] = val

    def __repr__(self) -> str:
        return '%s{%s}' % (self.__class__.__name__,
                           ', '.join([
                               '%r=%r' % (k, v) for k, v in list(self.items())
                           ]))

    def __getitem__(self, key: Union[str, int]) -> Any:
        return self._values[key]

    def __setitem__(self, key: Union[str, int], value: Any) -> Any:
        return self.add_item(key, value)

    def __delitem__(self, key: Union[str, int]) -> None:
        del self._values[key]
        self._order.remove(key)

    def __iter__(self) -> Iterator[Any]:
        return iter(self._order)

    def __len__(self) -> int:
        return len(self._order)

    def add_item(self,
                 key: Union[str, int],
                 value: Any,
                 after: bool = False,
                 index: Optional[int] = None,
                 pos_key: Union[None, str, int] = None,
                 replace: bool = True) -> None:
        """
        Add an item at a specific location, possibly replacing the
        existing item.

        If after is True, we insert *after* the given index, otherwise we
        insert before.

        The position is specified using either index or pos_key, the former
        specifies the position from the start of the array (base 0).  pos_key
        specifies the name of another key, and positions the new key relative
        to that key.

        When replacing, the position will be left un-changed unless a location
        is specified explicitly.
        """
        if self._validate_fn:
            self._validate_fn(value)

        if (index is not None) and (pos_key is not None):
            raise ValueError('Either specify index or pos_key, not both.')
        if pos_key is not None:
            try:
                index = self.index(pos_key)
            except ValueError:
                six.reraise(KeyError,
                            KeyError('%r not found' % pos_key),
                            sys.exc_info()[2])

        if after and (index is not None):
            # insert inserts *before* index, so increment by one.
            index += 1

        if key in self._values:
            if not replace:
                raise KeyError('%r is duplicate' % key)

            if index is not None:
                # We are re-locating.
                del self[key]
            else:
                # We are updating
                self._values[key] = value
                return

        if index is not None:
            # Place at given position
            self._order.insert(index, key)
        else:
            # Place at end
            self._order.append(key)
        self._values[key] = value

    def at(self, index: int) -> Any:  # pylint: disable=C0103
        """
        Return the key at the given index.
        """
        return self._order[index]

    def value_at(self, index: int) -> Any:
        """
        Return the value at the given index.
        """
        return self[self.at(index)]

    def index(self, *args, **kwargs):
        return self._order.index(*args, **kwargs)

    def reverse(self) -> 'SortableDict':
        self._order.reverse()
        return self

    def sort(self, *args, **kwargs) -> 'SortableDict':
        self._order.sort(*args, **kwargs)
        return self

    def pop_at(self, index: int) -> Any:
        """
        Remove the key at the given index and return its value.
        """
        return self.pop(self.at(index))

    def copy(self) -> 'SortableDict':
        return copy.deepcopy(self)
