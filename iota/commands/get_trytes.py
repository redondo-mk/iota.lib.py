# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import filters as f

from iota.commands import FilterCommand, RequestFilter, ResponseFilter
from iota.filters import Trytes
from iota.types import TransactionId

__all__ = [
  'GetTrytesCommand',
]


class GetTrytesCommand(FilterCommand):
  """
  Executes ``getTrytes`` command.

  See :py:method:`iota.api.StrictIota.get_trytes`.
  """
  command = 'getTrytes'

  def get_request_filter(self):
    return GetTrytesRequestFilter()

  def get_response_filter(self):
    return GetTrytesResponseFilter()


class GetTrytesRequestFilter(RequestFilter):
  def __init__(self):
    super(GetTrytesRequestFilter, self).__init__({
      'hashes': (
          f.Required
        | f.Array
        | f.FilterRepeater(f.Required | Trytes(result_type=TransactionId))
      ),
    })


class GetTrytesResponseFilter(ResponseFilter):
  def __init__(self):
    super(GetTrytesResponseFilter, self).__init__({
      'trytes': (
          f.Array
        | f.FilterRepeater(f.ByteString(encoding='ascii') | Trytes)
      ),
    })
