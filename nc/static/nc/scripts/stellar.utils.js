function getTxFee(numOrders) {
  /*
  Returns the transaction fee in XLM for a tx with numOrders orders
  in the transaction
  https://www.stellar.org/developers/guides/concepts/fees.html#transaction-fee
  */
  return numOrders * STELLAR_BASE_FEE;
}

function getMinBalance(account) {
  /*
  Determines and returns the minimum required balance for a given account.
  https://www.stellar.org/developers/guides/concepts/fees.html#minimum-account-balance
  https://www.stellar.org/developers/guides/concepts/ledger.html#account-entry
  */
  return STELLAR_BASE_RESERVE * (2 + account.subentry_count);
}

function isValidFederationAddress(address) {
  /*
  Determines whether given address is a valid Stellar federation address.
  */
  var re = /^(([^<>()[\]\\.,;:\s\*\"]+(\.[^<>()[\]\\.,;:\s\*\"]+)*)|(\".+\"))\*((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
  return re.test(address);
}

function isValidMemo(memo) {
  /*
  Determines whether the given memo is valid.

  NOTE: For now, simply assumes the memo is of type TEXT.
  */
  return (new TextEncoder('utf-8').encode(memo)).length <= STELLAR_MEMO_TEXT_BYTE_MAX;
}
