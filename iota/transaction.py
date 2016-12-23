# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from calendar import timegm as unix_timestamp
from datetime import datetime
from typing import Generator, Iterable, List, MutableSequence, \
  Optional, Tuple

from iota import Address, Hash, Tag, TrytesCompatible, TryteString, \
  int_from_trits, trits_from_int
from iota.crypto import Curl, HASH_LENGTH
from iota.crypto.addresses import AddressGenerator
from iota.crypto.signing import KeyGenerator, SignatureFragmentGenerator
from iota.exceptions import with_context

__all__ = [
  'Bundle',
  'BundleHash',
  'ProposedBundle',
  'ProposedTransaction',
  'Transaction',
  'TransactionHash',
]


# Custom types for type hints and docstrings.
Bundle = Iterable['Transaction']


class BundleHash(Hash):
  """
  A TryteString that acts as a bundle hash.
  """
  pass


class TransactionHash(Hash):
  """
  A TryteString that acts as a transaction hash.
  """
  pass


class ProposedTransaction(object):
  """
  A transaction that has not yet been attached to the Tangle.

  Provide to :py:meth:`iota.api.Iota.prepare_transfers` to attach to
  tangle and publish/store.
  """
  MESSAGE_LEN = 2187
  """
  Max number of trytes allowed in a transaction message.

  If a transaction's message is longer than this, it will be split into
  multiple transactions automatically when it is added to a bundle.

  See :py:meth:`ProposedBundle.add_transaction` for more info.
  """

  def __init__(self, address, value, tag=None, message=None, timestamp=None):
    # type: (Address, int, Optional[Tag], Optional[TrytesCompatible], Optional[int]) -> None
    super(ProposedTransaction, self).__init__()

    # See :py:class:`Transaction` for descriptions of these attributes.
    self.address  = address
    self.message  = TryteString(message or b'', pad=2187)
    self.tag      = Tag(tag or b'')
    self.value    = value

    # Python 3.3 introduced a :py:meth:`datetime.timestamp` method,
    # but for compatibility with Python 2, we have to do this the
    # old-fashioned way.
    # :see: http://stackoverflow.com/q/2775864/
    self.timestamp = timestamp or unix_timestamp(datetime.utcnow().timetuple())

    # These attributes are set by :py:meth:`ProposedBundle.finalize`.
    self.current_index              = None # type: Optional[int]
    self.last_index                 = None # type: Optional[int]
    self.trunk_transaction_hash     = None # type: Optional[TransactionHash]
    self.branch_transaction_hash    = None # type: Optional[TransactionHash]
    self.signature_message_fragment = None # type: Optional[TryteString]
    self.nonce                      = None # type: Optional[Hash]

  @property
  def timestamp_trits(self):
    # type: () -> List[int]
    """
    Returns the ``timestamp`` attribute expressed as trits.
    """
    return trits_from_int(self.timestamp, pad=27)

  @property
  def value_trits(self):
    # type: () -> List[int]
    """
    Returns the ``value`` attribute expressed as trits.
    """
    return trits_from_int(self.value, pad=81)

  @property
  def current_index_trits(self):
    # type: () -> List[int]
    """
    Returns the ``current_index`` attribute expressed as trits.
    """
    return trits_from_int(self.current_index, pad=27)

  @property
  def last_index_trits(self):
    # type: () -> List[int]
    """
    Returns the ``last_index`` attribute expressed as trits.
    """
    return trits_from_int(self.last_index, pad=27)


class ProposedBundle(object):
  """
  A collection of proposed transactions, to be treated as an atomic
  unit when attached to the Tangle.

  Conceptually, a bundle is similar to a block in a blockchain.
  """
  def __init__(self, transactions=None):
    # type: (Optional[Iterable[ProposedTransaction]]) -> None
    super(ProposedBundle, self).__init__()

    self.hash = None # type: Optional[Hash]
    self.tag  = None # type: Optional[Tag]

    self._transactions = [] # type: List[ProposedTransaction]

    if transactions:
      for t in transactions:
        self.add_transaction(t)

  @property
  def balance(self):
    # type: () -> int
    """
    Returns the bundle balance.
    In order for a bundle to be valid, its balance must be 0:

      - A positive balance means that there aren't enough inputs to
        cover the spent amount.
        Add more inputs using :py:meth:`add_inputs`.
      - A negative balance means that there are unspent inputs.
        Use :py:meth:`send_unspent_inputs_to` to send the unspent
        inputs to a "change" address.
    """
    return sum(t.value for t in self._transactions)

  def __len__(self):
    # type: () -> int
    """
    Returns te number of transactions in the bundle.
    """
    return len(self._transactions)

  def __iter__(self):
    # type: () -> Generator[ProposedTransaction]
    """
    Iterates over transactions in the bundle.
    """
    return iter(self._transactions)

  def __getitem__(self, index):
    # type: (int) -> ProposedTransaction
    """
    Returns the transaction at the specified index.
    """
    return self._transactions[index]

  def add_transaction(self, transaction):
    # type: (ProposedTransaction) -> None
    """
    Adds a transaction to the bundle.

    If the transaction message is too long, it will be split
    automatically into multiple transactions.
    """
    if self.hash:
      raise RuntimeError('Bundle is already finalized.')

    if transaction.value < 0:
      raise ValueError('Use ``add_inputs`` to add inputs to the bundle.')

    self._transactions.append(ProposedTransaction(
      address   = transaction.address,
      value     = transaction.value,
      tag       = transaction.tag,
      message   = transaction.message[:ProposedTransaction.MESSAGE_LEN],
      timestamp = transaction.timestamp,
    ))

    # Last-added transaction determines the bundle tag.
    self.tag = transaction.tag or self.tag

    # If the message is too long to fit in a single transactions,
    # it must be split up into multiple transactions so that it will
    # fit.
    fragment = transaction.message[ProposedTransaction.MESSAGE_LEN:]
    while fragment:
      self._transactions.append(ProposedTransaction(
        address   = transaction.address,
        value     = 0,
        tag       = transaction.tag,
        message   = fragment[:ProposedTransaction.MESSAGE_LEN],
        timestamp = transaction.timestamp,
      ))

      fragment = fragment[ProposedTransaction.MESSAGE_LEN:]

  def add_inputs(self, inputs):
    # type: (Iterable[Address]) -> None
    """
    Adds inputs to spend in the bundle.

    Note that each input requires two transactions, in order to
    hold the entire signature.

    :param inputs:
      Addresses to use as the inputs for this bundle.

      IMPORTANT: Must have ``balance`` and ``key_index`` attributes!
      Use :py:meth:`iota.api.get_inputs` to prepare inputs.
    """
    if self.hash:
      raise RuntimeError('Bundle is already finalized.')

    for addy in inputs:
      if addy.balance is None:
        raise with_context(
          exc = ValueError(
            'Address {address} has null ``balance`` '
            '(``exc.context`` has more info).'.format(
              address = addy,
            ),
          ),

          context = {
            'address': addy,
          },
        )

      if addy.key_index is None:
        raise with_context(
          exc = ValueError(
            'Address {address} has null ``key_index`` '
            '(``exc.context`` has more info).'.format(
              address = addy,
            ),
          ),

          context = {
            'address': addy,
          },
        )

      # Add the input as a transaction.
      self.add_transaction(ProposedTransaction(
        address = addy,
        value   = -addy.balance,
        tag     = self.tag,
      ))

      # Signatures require multiple transactions to store, due to
      # transaction length limit.
      for _ in range(AddressGenerator.DIGEST_ITERATIONS):
        self.add_transaction(ProposedTransaction(
          address = addy,
          value   = 0,
          tag     = self.tag,
        ))

  def send_unspent_inputs_to(self, address):
    # type: (Address) -> None
    """
    Adds a transaction to send "change" (unspent inputs) to the
    specified address.

    If the bundle has no unspent inputs, this method does nothing.
    """
    if self.hash:
      raise RuntimeError('Bundle is already finalized.')

    # Negative balance means that there are unspent inputs.
    # See :py:meth:`balance` for more info.
    unspent_inputs = -self.balance

    if unspent_inputs > 0:
      self.add_transaction(ProposedTransaction(
        address = address,
        value   = unspent_inputs,
        tag     = self.tag,
      ))

  def finalize(self):
    # type: () -> None
    """
    Finalizes the bundle, preparing it to be attached to the Tangle.
    """
    if self.hash:
      raise RuntimeError('Bundle is already finalized.')

    balance = self.balance
    if balance > 0:
      raise ValueError(
        'Inputs are insufficient to cover bundle spend '
        '(balance: {balance}).'.format(
          balance = balance,
        ),
      )
    elif balance < 0:
      raise ValueError(
        'Bundle has unspent inputs (balance: {balance}).'.format(
          balance = balance,
        ),
      )

    sponge      = Curl()
    last_index  = len(self) - 1

    for (i, t) in enumerate(self): # type: Tuple[int, ProposedTransaction]
      t.current_index = i
      t.last_index    = last_index

      sponge.absorb(
          # Ensure address checksum is not included in the result.
          t.address.address.as_trits()
        + t.value_trits
        + t.tag.as_trits()
        + t.timestamp_trits
        + t.current_index_trits
        + t.last_index_trits
      )

    bundle_hash = [0] * HASH_LENGTH # type: MutableSequence[int]
    sponge.squeeze(bundle_hash)
    self.hash = Hash.from_trits(bundle_hash)

    for t in self:
      t.bundle_hash = self.hash

  def sign_inputs(self, key_generator):
    # type: (KeyGenerator) -> None
    """
    Sign inputs in a finalized bundle.
    """
    if not self.hash:
      raise RuntimeError('Cannot sign inputs until bundle is finalized.')

    # Use a counter for the loop so that we can skip ahead as we go.
    i = 0
    while i < len(self):
      txn = self[i]

      if txn.value < 0:
        # In order to sign the input, we need to know the index of
        # the private key used to generate it.
        if txn.address.key_index is None:
          raise with_context(
            exc = ValueError(
              'Unable to sign input {input}; ``key_index`` is None '
              '(``exc.context`` has more info).'.format(
                input = txn.address,
              ),
            ),

            context = {
              'transaction': txn,
            },
          )

        signature_fragment_generator = SignatureFragmentGenerator(
          key_generator.get_keys(
            start       = txn.address.key_index,
            iterations  = AddressGenerator.DIGEST_ITERATIONS
          )[0],
        )

        hash_fragment_iterator = self.hash.iter_chunks(9)

        # We can only fit one signature fragment into each transaction,
        # so we have to split the entire signature among the extra
        # transactions we created for this input in
        # :py:meth:`add_inputs`.
        for j in range(AddressGenerator.DIGEST_ITERATIONS):
          self[i+j].signature_message_fragment =\
            signature_fragment_generator.send(next(hash_fragment_iterator))

        i += AddressGenerator.DIGEST_ITERATIONS - 1

      i += 1


class Transaction(object):
  """
  A transaction that has been attached to the Tangle.
  """
  @classmethod
  def from_tryte_string(cls, trytes):
    # type: (TrytesCompatible) -> Transaction
    """
    Creates a Transaction object from a sequence of trytes.
    """
    tryte_string = TryteString(trytes)

    hash_ = [0] * HASH_LENGTH # type: MutableSequence[int]

    sponge = Curl()
    sponge.absorb(tryte_string.as_trits())
    sponge.squeeze(hash_)

    return cls(
      hash_ = TransactionHash.from_trits(hash_),
      signature_message_fragment = tryte_string[0:2187],
      address = Address(tryte_string[2187:2268]),
      value = int_from_trits(tryte_string[2268:2295].as_trits()),
      tag = Tag(tryte_string[2295:2322]),
      timestamp = int_from_trits(tryte_string[2322:2331].as_trits()),
      current_index = int_from_trits(tryte_string[2331:2340].as_trits()),
      last_index = int_from_trits(tryte_string[2340:2349].as_trits()),
      bundle_id = BundleHash(tryte_string[2349:2430]),
      trunk_transaction_id = TransactionHash(tryte_string[2430:2511]),
      branch_transaction_id = TransactionHash(tryte_string[2511:2592]),
      nonce = Hash(tryte_string[2592:2673]),
    )

  def __init__(
      self,
      hash_,
      signature_message_fragment,
      address,
      value,
      tag,
      timestamp,
      current_index,
      last_index,
      bundle_id,
      trunk_transaction_id,
      branch_transaction_id,
      nonce,
  ):
    # type: (Hash, TryteString, Address, int, Tag, int, int, int, Hash, TransactionHash, TransactionHash, Hash) -> None
    self.hash = hash_
    """
    Transaction ID, generated by taking a hash of the transaction
    trits.
    """

    self.bundle_id = bundle_id
    """
    Bundle ID, generated by taking a hash of all the transactions in
    the bundle.
    """

    self.address = address
    """
    The address associated with this transaction.
    If ``value`` is != 0, the associated address' balance is adjusted
    as a result of this transaction.
    """

    self.value = value
    """
    Amount to adjust the balance of ``address``.
    Can be negative (i.e., for spending inputs).
    """

    self.tag = tag
    """
    Optional classification tag applied to this transaction.
    """

    self.nonce = nonce
    """
    Unique value used to increase security of the transaction hash.
    """

    self.timestamp = timestamp
    """
    Timestamp used to increase the security of the transaction hash.

    IMPORTANT: This value is easy to forge!
    Do not rely on it when resolving conflicts!
    """

    self.current_index = current_index
    """
    The position of the transaction inside the bundle.

    For value transfers, the "spend" transaction is generally in the
    0th position, followed by inputs, and the "change" transaction is
    last.
    """

    self.last_index = last_index
    """
    The position of the final transaction inside the bundle.
    """

    self.branch_transaction_id  = branch_transaction_id
    self.trunk_transaction_id   = trunk_transaction_id

    self.signature_message_fragment =\
      TryteString(signature_message_fragment or b'')
    """
    Cryptographic signature used to verify the transaction.

    Signatures are usually too long to fit into a single transaction,
    so they are split out into multiple transactions in the same bundle
    (hence it's called a fragment).
    """

    self.is_confirmed = None # type: Optional[bool]
    """
    Whether this transaction has been confirmed by neighbor nodes.
    Must be set manually via the ``getInclusionStates`` API command.

    References:
      - :py:meth:`iota.api.StrictIota.get_inclusion_states`
      - :py:meth:`iota.api.Iota.get_transfers`
    """

  @property
  def is_tail(self):
    # type: () -> bool
    """
    Returns whether this transaction is a tail.
    """
    return self.current_index == 0

  def as_tryte_string(self):
    # type: () -> TryteString
    """
    Returns a TryteString representation of the transaction.
    """
    return (
        self.signature_message_fragment
      + self.address
      + TryteString.from_trits(trits_from_int(self.value, pad=81))
      + self.tag
      + TryteString.from_trits(trits_from_int(self.timestamp, pad=27))
      + TryteString.from_trits(trits_from_int(self.current_index, pad=27))
      + TryteString.from_trits(trits_from_int(self.last_index, pad=27))
      + self.bundle_id
      + self.trunk_transaction_id
      + self.branch_transaction_id
      + self.nonce
    )
