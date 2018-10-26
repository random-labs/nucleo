(function() {
  /* Initialization of Stellar server */
  var server = new StellarSdk.Server(STELLAR_SERVER_URL);

  $(document).ready(function() {
    // Determine all the assets need info on for this profile
    let requiredAssets = getRelevantAssets();

    // Fetch compiled asset prices, vol, etc. from StellarTerm/Horizon
    // when ready.
    $.when(getTickerAssets(server, requiredAssets))
    .done(function(assets) {
      // Add in values for assets in terms of USD/XLM
      populateAssetValues(assets);

      // Aggregate portfolio allocation data then plot
      calculateAndPlotAssetAllocationValues(assets);
    });
  });

  function getRelevantAssets() {
    /*
    Fetch all the assets that need price related info on current document.
    */
    var assetIdSet = new Set([]);
    $('.asset-ticker').each(function(i, assetTickerDiv) {
      if (assetTickerDiv.hasAttribute('data-asset_id')) {
        assetIdSet.add(assetTickerDiv.dataset.asset_id);
      }
    });
    return Array.from(assetIdSet).map(function(assetId) {
      if (assetId != 'XLM-native') {
        return new StellarSdk.Asset(assetId.split('-')[0], assetId.split('-')[1]);
      } else {
        return StellarSdk.Asset.native();
      }
    });
  }

  function populateAssetValues(data) {
    /*
    Use ticker data = { asset.id: asset } to populate asset values
    in USD and 24h percent change for all assets in user's portfolio.
    */
    // Get all the asset price containers
    $('.asset-ticker').each(function(i, assetTickerDiv) {
      // For each check for an asset in the fetched data
      let asset = data[assetTickerDiv.dataset.asset_id];
      if (asset) {
        if (!$(assetTickerDiv).data('asset_balance')) {
          // Then simply filling in the price
          // If fetched asset exists, set USD, XLM val and % change
          // data as container text.
          let usdPrice = asset.price_USD,
              xlmPrice = asset.price_XLM,
              usdPercentChange = asset.change24h_USD/100,
              xlmPercentChange = asset.change24h_XLM/100;

          // Set inner content for asset values
          // NOTE: Not using numeral() to format here and
          // trusting StellarTerm returned price val for sig figs
          $(assetTickerDiv).find('.asset-price-usd').each(function(i, assetPriceUsd) {
            if (usdPrice) {
              assetPriceUsd.textContent = numeral(usdPrice).format('$0,0.0000');
              if (usdPercentChange > 0) {
                assetPriceUsd.classList.add('text-success');
              } else if (usdPercentChange < 0) {
                assetPriceUsd.classList.add('text-danger');
              }
            }
          });
          $(assetTickerDiv).find('.asset-price-xlm').each(function(i, assetPriceXlm) {
            // NOTE: check if xlmPrice is even there given some assets mirror XLM (and don't give this attr)
            if (xlmPrice) {
              assetPriceXlm.textContent = xlmPrice + ' XLM';
              if (xlmPercentChange > 0) {
                assetPriceXlm.classList.add('text-success');
              } else if (xlmPercentChange < 0) {
                assetPriceXlm.classList.add('text-danger');
              }
            }
          });
        } else {
          // Building the balance ticker div
          // If fetched asset exists, set val and % change
          // data as container text.
          var value, valueText, percentChange, valueChange, valueChangeText;
          // Reference to USD val and % change
          value = asset.price_USD * parseFloat(assetTickerDiv.dataset.asset_balance);
          valueText = numeral(value).format('$0,0.00');
          percentChange = asset.change24h_USD/100;
          valueChange = value * percentChange;
          valueChangeText = numeral(valueChange).format('$0,0.00');

          // Create the asset value div and append to ticker div
          assetValueDiv = document.createElement('div');
          assetValueDiv.classList.add('text-muted');
          assetValueDiv.textContent = valueText;
          assetTickerDiv.appendChild(assetValueDiv);

          // Create the 24H change div
          assetChangeDiv = document.createElement('small');
          assetChangeDiv.setAttribute('title', 'Change 24h');
          assetChangeDiv.classList.add('font-weight-bold');
          changeText = (percentChange > 0 ? valueChangeText + ' (+' + numeral(percentChange).format('0.00%') + ')' : valueChangeText + ' (' + numeral(percentChange).format('0.00%') + ')');
          assetChangeText = document.createTextNode(changeText);
          assetChangeDiv.appendChild(assetChangeText);

          // Change asset value color depending
          // on % change (if exactly zero, don't add color).
          if (percentChange > 0) {
            assetChangeDiv.classList.add('text-success');
          } else if (percentChange < 0) {
            assetChangeDiv.classList.add('text-danger');
          }

          // Append change div to asset ticker
          assetTickerDiv.appendChild(assetChangeDiv);
        }

        // Make the full ticker div visible
        $(assetTickerDiv).fadeIn();
      }
    });
  }

  function calculateAndPlotAssetAllocationValues(data) {
    /*
    Use ticker data = { asset.id: asset } to populate asset allocation
    percentages then plot in allocation chart.
    */
    // Determine current value of portfolio assets using all the asset price containers
    var totalValue = 0.0, portfolioValues = {};
    $('.asset-ticker').each(function(i, assetTickerDiv) {
      // For each check for an asset in the fetched data
      let asset = data[assetTickerDiv.dataset.asset_id];
      if (asset) {
        let value = asset.price_USD * parseFloat(assetTickerDiv.dataset.asset_balance);
        if (value > 0.0) {
          portfolioValues[asset.id] = value;
          totalValue += value;
        }
      }
    });

    // Chart data in USD value
    if (totalValue > 0.0) {
      var seriesData = [];
      Object.keys(portfolioValues).forEach(function(assetId) {
        var name = assetId;
        if (assetId != 'XLM-native') {
          let nameSplit = name.split('-');
          name = nameSplit[0] + '-' + nameSplit[1].substring(0, 5) + '...' + nameSplit[1].substring(nameSplit[1].length - 5);
        }
        seriesData.push({
          name: name,
          y: portfolioValues[assetId]
        });
      });
      $('.asset-allocation-chart').each(function(i, assetAllocationChartDiv) {
        createAssetAllocationChart(assetAllocationChartDiv.id, 'Asset Allocation', seriesData);
      });
    }
  }

  function createAssetAllocationChart(containerId, seriesName, seriesData) {
    /**
    * Create the chart when all data is loaded into seriesOptions
    */
    Highcharts.chart(containerId, {
      chart: {
        plotBackgroundColor: null,
        plotBorderWidth: null,
        plotShadow: false,
        type: 'pie'
      },
      title: {
        text: ''
      },
      tooltip: {
          pointFormat: '{series.name}: <b>$ {point.y:,.2f}</b>'
      },
      plotOptions: {
          pie: {
              allowPointSelect: true,
              cursor: 'pointer',
              dataLabels: {
                  enabled: true,
                  format: '<b>{point.name}</b>: {point.percentage:.2f} %',
                  style: {
                      color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
                  }
              }
          }
      },
      series: [{
        name: seriesName,
        colorByPoint: true,
        data: seriesData,
      }]
    });
  }

  if (IS_CURRENT_USER) {
    /** Initialization of forms **/
    function resetStellarForms() {
      // NOTE: If don't have minimum number of accts, this form won't be on html template
      let issueStellarModalForm = $('#issueStellarModalForm')[0];
      if (issueStellarModalForm) {
        issueStellarModalForm.reset();
      }
    };

    /* Gets user account public keys this user has already associated */
    function getUserAccountPublicKeys() {
      return CURRENT_USER_PUBLIC_KEYS;
    };

    $(document).ready(function() {
      // If IS_CURRENT_USER, add to document ready
      // resetting the Stellar issue asset forms
      resetStellarForms();
    });

    /** Bootstrap issueStellarModalForm close **/
    $('#issueStellarModal').on('hidden.bs.modal', function (e) {
      // Clear out forms
      resetStellarForms();
    });

    /** Bootstrap issueStellarModalForm submission **/
    $('#issueStellarModalForm').submit(function(event) {
      event.preventDefault();

      // Obtain the modal header to display errors under if POSTings fail
      let modalHeader = $(this).find('.modal-body-header')[0];

      // Attempt to generate Keypairs
      var issuingKeys, distributionKeys;
      try {
        issuingKeys = StellarSdk.Keypair.fromSecret(this.elements["issuer_secret_key"].value);
      }
      catch (err) {
        console.error('Keypair generation failed', err);
        displayError(modalHeader, 'Keypair generation failed for the issuing account. Please enter a valid secret key.');
        return false;
      }
      try {
        distributionKeys = StellarSdk.Keypair.fromSecret(this.elements["distributer_secret_key"].value);
      }
      catch (err) {
        console.error('Keypair generation failed', err);
        displayError(modalHeader, 'Keypair generation failed for the distribution account. Please enter a valid secret key.');
        return false;
      }

      // Check that both issuing and distribution accounts have been associated with Nucleo db
      // and they aren't the same.
      let userAccountPublicKeys = getUserAccountPublicKeys();
      if (!userAccountPublicKeys.includes(issuingKeys.publicKey()) || !userAccountPublicKeys.includes(distributionKeys.publicKey())) {
        displayError(modalHeader, 'Both distribution and issuing accounts must be associated with your user profile.');
        return false;
      } else if (issuingKeys.publicKey() == distributionKeys.publicKey()) {
        displayError(modalHeader, 'Your distribution account must be different than your issuing account.');
        return false;
      }

      // Store the user inputted asset detail values and the success redirect URL
      let tokenCode = this.elements["token_code"].value,
          numberOfTokens = this.elements["token_number"].value,
          issuerHomeDomain = this.elements["issuer_domain"].value;

      // If successful on KeyPair generation, load account to prep for manage data transaction
      // Start Ladda animation for UI loading
      let laddaButton = Ladda.create($(this).find(":submit")[0]);
      laddaButton.start();

      // Load distribution then issuing account from Horizon server
      server.loadAccount(distributionKeys.publicKey())
      .catch(StellarSdk.NotFoundError, function (error) {
        throw new Error('No Stellar account with the distribution secret key exists yet.');
      })
      .then(function(distributionAccount) {
        server.loadAccount(issuingKeys.publicKey())
        .catch(StellarSdk.NotFoundError, function (error) {
          throw new Error('No Stellar account with the issuing secret key exists yet.');
        })
        // If there was no error, load up-to-date information on your account.
        .then(function(issuingAccount) {
          // Create the asset
          var asset = new StellarSdk.Asset(tokenCode, issuingKeys.publicKey())

          // Start building the transaction.
          transaction = new StellarSdk.TransactionBuilder(issuingAccount)
            .addOperation(StellarSdk.Operation.changeTrust({
              'asset': asset,
              'limit': numberOfTokens,
              'source': distributionKeys.publicKey(),
            }))
            .addOperation(StellarSdk.Operation.payment({
              'destination': distributionKeys.publicKey(),
              'asset': asset,
              'amount': numberOfTokens,
            }))
            .addOperation(StellarSdk.Operation.setOptions({
              'homeDomain': issuerHomeDomain,
            }))
            .build();

          // Instantiate client side event listener to verify
          // transaction has settled.
          var es = server.operations().cursor('now').forAccount(issuingAccount.id)
            .stream({
            onmessage: function (op) {
              if (op.source_account == issuingAccount.id && op.type_i == STELLAR_OPERATION_PAYMENT
                && op.asset_code == asset.code && op.asset_issuer == asset.issuer) {
                // Close the event stream connection
                es();

                // Notify user of successful submission
                displaySuccess(modalHeader, 'Successfully submitted transaction to the Stellar network.');

                // Submit the tx hash to Nucleo servers to create
                // activity in user feeds
                let activityForm = $('#activityForm')[0];
                activityForm.elements["tx_hash"].value = op.transaction_hash;
                activityForm.submit();
              }
            }
          });

          // Sign the transaction to prove you are actually the person sending it.
          transaction.sign(issuingKeys, distributionKeys);

          // And finally, send it off to Stellar! Check for StellarGuard protection.
          return server.submitTransaction(transaction);
        })
        .catch(function(error) {
          // Stop the button loading animation then display the error
          laddaButton.stop();
          console.error('Something went wrong with Stellar call', error);
          displayError(modalHeader, error.message);
          return false;
        });
      })
      .then(function(result) {
        let message = 'Confirming transaction settlement ...';
        displayWarning(modalHeader, message);
      })
      .catch(function(error) {
        // Stop the button loading animation then display the error
        laddaButton.stop();
        console.error('Something went wrong with Stellar call', error);
        displayError(modalHeader, error.message);
        return false;
      });
    });
  }
})();
