(function() {
  var streamClient, streamFeed;

  /*
  Initialize Stream client and get current user timeline.
  */
  $(document).ready(function() {
    streamClient = stream.connect(STREAM_API_KEY, null);
    streamFeed = streamClient.feed(STREAM_FEED_TYPE, STREAM_FEED_ID, STREAM_FEED_TOKEN);

    // Load the first batch of activities by clicking the "more" button
    let moreButton = $('#moreButton');
    if (moreButton) {
      moreButton.click();
    }
  });

  /** Load more activity items when the MORE button is clicked **/
  $('button.more-feed').on('click', function() {
    // Get the more button container to prep for DOM
    // insertion before the div (in the activityList)
    let button = this;

    // If data-has_more has been set to "false", MORE button is at the end
    // of all records from Horizon, so don't bother fetching
    if (button.dataset.has_more == "true") {
      // Only load more if records left
      var activityListQuery = $(button.dataset.parent);

      // TODO: implement ascending/descending order for diff between activity and comment section

      // Set up ops for get call
      var ops = { limit: STREAM_FEED_LIMIT };
      if (button.dataset.id_lt) {
        ops["id_lt"] = button.dataset.id_lt;
      }

      // Get records, parse, then add to list of DOMs
      // TODO: Spin this GET call off into an endpoint on Nucleo servers like news list view?
      // if so, would then have the active media items for all relevant quantities.
      streamFeed.get(ops).then(function(resp) {
        // Resp Json has key, vals:
        // 'object': {'results': [ActivityItem], 'next': url, 'duration': "ms" },

        // Iterate through operation records parsing and appropriately formatting
        // the DOM object to add into newsList (before MORE button)
        var activities = [];
        resp.results.forEach(function(record) {
          activities.push(parseActivity(record));
        });

        // Append to end of newsList
        activityListQuery.append(activities);
        feather.replace(); // Call this so feather icons populate properly

        // If no next URL, then no more records to load
        if (resp.next == "") {
          button.dataset.id_lt = "";
          button.dataset.has_more = "false";
          button.classList.add("invisible");
        } else {
          // Otherwise, parse next URL for id_lt query param to store
          let nextUrl = new URL(resp.next, streamClient.baseUrl);
          button.dataset.id_lt = nextUrl.searchParams.get("id_lt");
          button.dataset.has_more = "true";
        }
      })
      .catch(function (err) {
        console.error('Unable to load feed activities', err);
      });
    }
  });

  // Attach the event listener for like/unlike button
  $('.btn-like').on('click', function() {
    let button = this;

    // Build the JSON data to be submitted
    var formData = {
      'activity_id': this.dataset.activity_id,
      'feed_type': this.dataset.feed_type,
    };

    // Submit it to Nucleo's create account endpoint
    // TODO: IMPLEMENT A LISTENER FOR SUCCESSFUL ADDITION TO FEED IF NOT
    // ALREADY LISTENING
    $.post(STREAM_FEED_LIKE_ACTION, formData)
    .then(function(result) {
      // Toggle like button color and like count
      button.classList.toggle('text-danger');
      button.classList.toggle('text-dark');

      // Get the current count, increment it by
      let countSmall = $(button).find("small")[0],
          countDelta = (button.classList.contains('text-danger') ? 1 : -1),
          count = parseInt(button.dataset.likes_count) + countDelta,
          countContent = ( count > 0 ? String(count) : "" );
      button.dataset.likes_count = count;
      countSmall.textContent = countContent;

      // Update the likes link in footer of activity detail
      if (button.dataset.child) {
        var likesA = $(button.dataset.child)[0],
            countSpan = $(button.dataset.child).find(".count")[0],
            pluralSpan = $(button.dataset.child).find(".plural")[0];

        countSpan.textContent = countContent;
        if (count == 0) {
          likesA.classList.add('d-none');
        } else if (count == 1) {
          likesA.classList.remove('d-none');
          pluralSpan.classList.add('d-none');
        } else {
          likesA.classList.remove('d-none');
          pluralSpan.classList.remove('d-none');
        }
      }
    })
    .catch(function(error) {
      // Fail response gives form.errors. Make sure to show in error form
      console.error('Something went wrong with Nucleo call', error);
    });
  });


  /** Parse activity record and format appropriately for activity list **/
  function parseActivity(record) {
    // Returns DOM element for insertion into activityList before MORE button
    // EXAMPLE:
    // <li class="list-group-item d-flex justify-content-between p-4">
    //   <div class="d-flex align-content-start">
    //     <div class="position-relative">
    //       <a href=""><img class="img-object-fit-cover rounded" style="height: 60px; width: 60px;" src="{{ profile.pic.url }}" alt=""></a>
    //       <a href=""><img class="img-object-fit-cover img-thumbnail rounded-circle position-absolute" style="height: 40px; width: 40px; top: -15px; left: -15px;" src="{% static 'nc/images/rocket.png' %}" alt=""></a>
    //     </div>
    //     <div class="d-flex flex-column align-items-start mx-3">
    //       <a href="" class="d-flex flex-column align-items-start list-group-item list-group-item-action">
    //        <span><a href="" class="text-dark font-weight-bold">@mikey.rf</a> sent 0.75 <a href="" class="text-dark font-weight-bold">XLM</a> to <a href="" class="text-dark font-weight-bold">@feld27</a></span>
    //        <div class="h3 pt-2">Memo!</div>
    //        <div><small class="text-muted">15 days ago</small></div>
    //        <div><small>Tx #: <a href="https://horizon-testnet.stellar.org/transactions/bfaf2287695c651747e635ca7e03698ba44611ed9a6b919bd1db9727a0b6dfda" class="text-info" title="Stellar Transaction Hash" target="_blank">bfaf221...0b6dfda</a></small></div>
    //       </a>
    //       <div class="d-flex flex-row justify-content-start mt-2">
    //        <div class="pr-4"><button class="btn btn-link btn-like text-danger p-0" data-activity_id="a8ad2b80-ca6c-11e8-8080-8001503994dc" data-likes_count="2"><span data-feather="heart"></span><small class="pl-1">2</small></button></div>
    //        <div class="pr-4"><button class="btn btn-link btn-reward text-dark p-0" data-activity_id="a8ad2b80-ca6c-11e8-8080-8001503994dc" data-rewards_total="2" data-toggle="modal" data-target="#rewardActivityModal"><span data-feather="award"></span><small class="pl-1">100</small></button></div>
    //        <div class="pr-4"><a href="" class="btn btn-link btn-comment text-dark p-0" data-activity_id="a8ad2b80-ca6c-11e8-8080-8001503994dc" data-comments_count="2"><span data-feather="message-circle"></span><small class="pl-1">7</small></button></div>
    //       </div>
    //     </div>
    //   </div>
    //   <span data-feather="send"></span>
    // </li>

    // Build the full DOM li list item object
    var li = document.createElement("li");
    li.setAttribute("class", "list-group-item d-flex justify-content-between p-4");

    var contentDiv = document.createElement("div");
    contentDiv.setAttribute("class", "d-flex align-content-start");
    li.append(contentDiv);

    // Profile pic container for relevant image(s): actor pic
    // and object/asset pic
    var picContentDiv = document.createElement("div");
    picContentDiv.setAttribute("class", "position-relative");

    var actorPicA = document.createElement("a");
    actorPicA.setAttribute("href", record.actor_href);

    var actorPicImg = document.createElement("img");
    actorPicImg.setAttribute("class", "img-object-fit-cover rounded");
    actorPicImg.style.width = "60px";
    actorPicImg.style.height = "60px";
    if (record.actor_pic_url) {
      actorPicImg.setAttribute("src", record.actor_pic_url);
    }
    actorPicA.append(actorPicImg);
    picContentDiv.append(actorPicA);
    contentDiv.append(picContentDiv);

    if (record.verb != 'post' && record.verb != 'comment') {
      let otherHrefAttribute = (record.verb == 'send' ? 'asset_href' : 'object_href'),
          otherPicUrlAttribute = (record.verb == 'send' ? 'asset_pic_url' : 'object_pic_url'),
          otherHasHref = otherHrefAttribute in record,
          otherHasPicUrl = otherPicUrlAttribute in record;

      var otherPicA = document.createElement("a");
      // Check whether object/asset has been registered in Nucleo db
      if (otherHasHref) {
        otherPicA.setAttribute("href", record[otherHrefAttribute]);
      }

      var otherPicImg = document.createElement("img");
      if (record.verb == 'follow') {
        otherPicImg.setAttribute("class", "img-object-fit-cover img-thumbnail rounded position-absolute");
      } else {
        otherPicImg.setAttribute("class", "img-object-fit-cover img-thumbnail rounded-circle position-absolute");
      }
      otherPicImg.style.height = "40px";
      otherPicImg.style.width = "40px";
      otherPicImg.style.top = "-15px";
      otherPicImg.style.left = "-15px";
      if (otherHasPicUrl) {
        otherPicImg.setAttribute("src", record[otherPicUrlAttribute]);
      }
      otherPicA.append(otherPicImg);
      picContentDiv.append(otherPicA);
    }
    contentDiv.append(picContentDiv);

    // Description container for all the relevant
    // activity details
    var descriptionContentDiv = document.createElement("div"),
        descriptionContentA = document.createElement("a");
    descriptionContentDiv.setAttribute("class", "d-flex flex-column align-items-start mx-3");
    descriptionContentA.setAttribute("class", "d-flex flex-column align-items-start list-group-item list-group-item-action p-0 m-0 border-0");
    if (record.activity_url) {
      descriptionContentA.setAttribute("href", record.activity_url);
    }
    descriptionContentDiv.append(descriptionContentA);
    contentDiv.append(descriptionContentDiv);

    var descriptionSpan = document.createElement("span"),
        memoDiv = document.createElement("div"),
        memoContent = ((record.memo || record.message) ? (record.memo ? record.memo : record.message) : ""),
        memoText = document.createTextNode(memoContent),
        timeSinceDiv = document.createElement("div"),
        timeSinceSmall = document.createElement("small"),
        timeSince = moment(record.time + "Z").fromNow(), // NOTE: Stellar horizon created_at attribute stored in stream record.time implicitly assumes UTC so add Z here
        timeSinceText = document.createTextNode(timeSince),
        actionsDiv = document.createElement("div"),
        actionLikeContainer = document.createElement("div"),
        actionRewardContainer = document.createElement("div"),
        actionCommentContainer = document.createElement("div"),
        actionLikeButton = document.createElement("button"),
        actionRewardButton = document.createElement("button"),
        actionCommentButton = document.createElement("a"),
        actionLikeIconSpan = document.createElement("span"),
        actionRewardIconSpan = document.createElement("span"),
        actionCommentIconSpan = document.createElement("span"),
        actionLikeSmall = document.createElement("small"),
        actionRewardSmall = document.createElement("small"),
        actionCommentSmall = document.createElement("small"),
        actionLikeContent = (record.likes_count && record.likes_count > 0 ? record.likes_count : ""),
        actionRewardContent = (record.rewards_total && record.rewards_total > 0 ? record.rewards_total : ""),
        actionCommentContent = (record.comments_count && record.comments_count > 0 ? record.comments_count : ""),
        actionLikeText = document.createTextNode(actionLikeContent),
        actionRewardText = document.createTextNode(actionRewardContent),
        actionCommentText = document.createTextNode(actionCommentContent);

    // Description span in description container
    descriptionSpan.setAttribute("style", "font-size: 0.9em")

    // Memo div in description container
    if (record.verb != 'comment') {
      memoDiv.setAttribute("class", "h3 pt-2 text-dark");
    } else {
      memoDiv.setAttribute("class", "h5 pt-2 text-dark");
    }
    memoDiv.appendChild(memoText);

    // Timesince div in description container
    timeSinceSmall.setAttribute("class", "text-muted");
    timeSinceSmall.appendChild(timeSinceText);
    timeSinceDiv.appendChild(timeSinceSmall);

    // Append description, memo, and time since to outer description <a>
    descriptionContentA.append(descriptionSpan);
    descriptionContentA.append(memoDiv);
    descriptionContentA.append(timeSinceDiv);

    // Tx hash div in description container
    if (record.tx_hash) {
      let recordTxHash = record.tx_hash;
      var txHashDiv = document.createElement("div"),
          txHash = recordTxHash.substring(0, 7) + '...' + recordTxHash.substring(recordTxHash.length-7),
          txHashHref = STELLAR_EXPERT_TRANSACTION_URL + recordTxHash,
          txHashSmall = document.createElement("small"),
          txHashText = document.createTextNode("Tx #: "),
          txHashA = document.createElement("a"),
          txHashAText = document.createTextNode(txHash);

      txHashA.setAttribute("class", "text-info");
      txHashA.setAttribute("title", "Stellar Transaction Hash");
      txHashA.setAttribute("target", "_blank");
      txHashA.setAttribute("href", txHashHref);
      txHashA.appendChild(txHashAText);

      txHashDiv.appendChild(txHashSmall);
      txHashSmall.appendChild(txHashText);
      txHashSmall.appendChild(txHashA);
      txHashA.appendChild(txHashAText);
      descriptionContentA.append(txHashDiv);
    }

    // Like, comment and reward buttons in description container
    actionsDiv.setAttribute("class", "d-flex flex-row justify-content-start mt-2");

    actionLikeIconSpan.setAttribute("data-feather", "heart");
    actionLikeContainer.setAttribute("class", "pr-4");
    if (record.liked_by && record.liked_by.includes(CURRENT_USER_ID)) {
      actionLikeButton.setAttribute("class", "btn btn-link btn-like text-danger p-0");
    } else {
      actionLikeButton.setAttribute("class", "btn btn-link btn-like text-dark p-0");
    }
    // Set the data attributes needed for POST to like/unlike endpoint
    actionLikeButton.setAttribute("data-id", record.foreign_id);
    actionLikeButton.setAttribute("data-activity_id", record.id);
    actionLikeButton.setAttribute("data-feed_type", STREAM_FEED_TYPE);
    actionLikeButton.setAttribute("data-likes_count", (record.likes_count ? record.likes_count : 0));
    // Attach the event listener for like/unlike
    actionLikeButton.addEventListener('click', function() {
      let button = this;

      // Build the JSON data to be submitted
      var formData = {
        'activity_id': this.dataset.activity_id,
        'feed_type': this.dataset.feed_type,
      };

      // Submit it to Nucleo's create account endpoint
      // TODO: IMPLEMENT A LISTENER FOR SUCCESSFUL ADDITION TO FEED IF NOT
      // ALREADY LISTENING
      $.post(STREAM_FEED_LIKE_ACTION, formData)
      .then(function(result) {
        // Toggle like button color and like count
        button.classList.toggle('text-danger');
        button.classList.toggle('text-dark');

        // Get the current count, increment it by
        let countSmall = $(button).find("small")[0],
            countDelta = (button.classList.contains('text-danger') ? 1 : -1),
            count = parseInt(button.dataset.likes_count) + countDelta,
            countContent = ( count > 0 ? String(count) : "" );
        button.dataset.likes_count = count;
        countSmall.textContent = countContent;
      })
      .catch(function(error) {
        // Fail response gives form.errors. Make sure to show in error form
        console.error('Something went wrong with Nucleo call', error);
      });
    });
    // Append rest of DOM to button and container
    actionLikeSmall.setAttribute("class", "pl-1");
    actionLikeButton.append(actionLikeIconSpan);
    actionLikeSmall.append(actionLikeText);
    actionLikeButton.append(actionLikeSmall);
    actionLikeContainer.append(actionLikeButton);

    actionRewardIconSpan.setAttribute("data-feather", "award");
    actionRewardContainer.setAttribute("class", "pr-4");
    if (record.rewarded_by && record.rewarded_by.includes(CURRENT_USER_ID)) {
      actionRewardButton.setAttribute("class", "btn btn-link btn-reward text-warning p-0");
    } else {
      actionRewardButton.setAttribute("class", "btn btn-link btn-reward text-dark p-0");
    }
    // Set the data attributes needed for button click modal open to reward
    actionRewardButton.setAttribute("data-id", record.foreign_id);
    actionRewardButton.setAttribute("data-activity_id", record.id);
    actionRewardButton.setAttribute("data-rewards_total", (record.rewards_total ? record.rewards_total : 0));
    actionRewardButton.setAttribute("data-toggle", "modal");
    actionRewardButton.setAttribute("data-target", "#rewardActivityModal");
    // Append rest of DOM to button and container
    actionRewardSmall.setAttribute("class", "pl-1");
    actionRewardButton.append(actionRewardIconSpan);
    actionRewardSmall.append(actionRewardText);
    actionRewardButton.append(actionRewardSmall);
    actionRewardContainer.append(actionRewardButton);

    actionCommentIconSpan.setAttribute("data-feather", "message-circle");
    actionCommentContainer.setAttribute("class", "pr-4");
    if (record.commented_by && record.commented_by.includes(CURRENT_USER_ID)) {
      actionCommentButton.setAttribute("class", "btn btn-link btn-comment text-primary p-0");
    } else {
      actionCommentButton.setAttribute("class", "btn btn-link btn-comment text-dark p-0");
    }
    if (record.activity_url) {
      actionCommentButton.setAttribute("href", record.activity_url);
    }
    // Set the data attributes needed for button click modal open to reward
    actionCommentButton.setAttribute("data-id", record.foreign_id);
    actionCommentButton.setAttribute("data-activity_id", record.id);
    actionCommentButton.setAttribute("data-comments_count", (record.comments_count ? record.comments_count : 0));
    // Append rest of DOM to button and container
    actionCommentSmall.setAttribute("class", "pl-1");
    actionCommentButton.append(actionCommentIconSpan);
    actionCommentSmall.append(actionCommentText);
    actionCommentButton.append(actionCommentSmall);
    actionCommentContainer.append(actionCommentButton);

    actionsDiv.appendChild(actionLikeContainer);
    // actionsDiv.appendChild(actionRewardContainer);
    if (record.verb != 'comment') {
      actionsDiv.appendChild(actionCommentContainer);
    }

    if (record.foreign_id) {
      // Only allow actions if there's an associated activity detail
      // in our system
      descriptionContentDiv.append(actionsDiv);
    }

    // Feather icon container for activity icon type
    var featherIconSpan = document.createElement("span");
    // li.append(featherIconSpan);

    // Determine feather icon and fill in description details
    // Four activity verb types
    //    1. Payments (verb: send)
    //    2. Token issuance (verb: issue)
    //    3. Buy/sell of asset (verb: offer)
    //    4. Follow user (verb: follow)
    //    5. Post on timeline (verb: post)
    //    6. Comment on post in timeline (verb: comment)
    //    7. Trust a new asset (verb: trust)
    var featherIcon, assetText,
        actorA = document.createElement("a"),
        objectA = document.createElement("a");

    actorA.setAttribute("class", "text-dark font-weight-bold");
    actorA.setAttribute("href", record.actor_href);
    actorA.append(document.createTextNode("@" + record.actor_username));

    objectA.setAttribute("class", "text-dark font-weight-bold");
    if (record.object_href) {
      objectA.setAttribute("href", record.object_href);
    }

    switch(record.verb) {
      case "send":
        // Sending payment to user
        // e.x.: <span><a href="" class="text-dark font-weight-bold">@mikey.rf</a> sent 0.75 <a href="" class="text-dark font-weight-bold">XLM</a> to <a href="" class="text-dark font-weight-bold">@feld27</a></span>
        featherIcon = "send";
        let objectText = (record.object_username ? "@" + record.object_username : record.object.substring(0, 7) + '...' + record.object.substring(record.object.length-7)); // NOTE: object is public_key if object_username is null (out of Nucleo db account)
        objectA.append(document.createTextNode(objectText));

        // Asset code a
        assetA = document.createElement("a");
        assetA.setAttribute("class", "text-dark font-weight-bold");
        if (record.asset_href) {
          assetA.setAttribute("href", record.asset_href);
        }
        assetText = (record.asset_type == 'native'? 'XLM': record.asset_code);
        assetA.append(document.createTextNode(assetText));

        descriptionSpan.append(actorA);
        descriptionSpan.append(document.createTextNode(" sent " + record.amount + " "));
        descriptionSpan.append(assetA);
        descriptionSpan.append(document.createTextNode(" to "));
        descriptionSpan.append(objectA);
        break;
      case "issue":
        // Token issuance
        // e.x.: <span>Tokens issued: <a href="" class="text-dark font-weight-bold">@mikey.rf</a> issued 1000 new <a href="" class="text-dark font-weight-bold">NUCL</a> from <a href="" class="text-info" target="_blank">GXJOSFOF...OJFSOFJ</a></span>
        featherIcon = "anchor";

        assetText = (record.object_type == 'native'? 'XLM': record.object_code);
        objectA.append(document.createTextNode(assetText));

        // New tokens title
        var tokenSpan = document.createElement("span");
        tokenSpan.setAttribute("class", "font-italic");
        tokenSpan.append(document.createTextNode("New tokens: "))

        // Account issuer a
        var accountA = document.createElement("a"),
            accountHref = STELLAR_EXPERT_ACCOUNT_URL + record.object_issuer,
            accountPublicKey = record.object_issuer.substring(0, 7) + '...' + record.object_issuer.substring(record.object_issuer.length-7);
        accountA.setAttribute("class", "text-info");
        accountA.setAttribute("target", "_blank");
        accountA.setAttribute("href", accountHref);
        accountA.append(document.createTextNode(accountPublicKey));

        descriptionSpan.append(tokenSpan);
        descriptionSpan.append(actorA);
        descriptionSpan.append(document.createTextNode(" issued " + record.amount + " "));
        descriptionSpan.append(objectA);
        descriptionSpan.append(document.createTextNode(" from "));
        descriptionSpan.append(accountA);
        break;
      case "offer":
        // Trading offers
        // e.x.: <span><a href="" class="text-dark font-weight-bold">@mikey.rf</a> bought/sold 100.00 <a href="" class="text-dark font-weight-bold">MOBI</a> at a price of 4.132 XLM</span>
        featherIcon = "trending-up";

        assetText = (record.object_type == 'native'? 'XLM': record.object_code);
        objectA.append(document.createTextNode(assetText));

        let action = (record.offer_type == "buying" ? 'offered to buy' : 'offered to sell'),
            amount = (record.offer_type == "buying" ? String(parseFloat(record.price) * parseFloat(record.amount)) : record.amount),
            priceSpan = document.createElement("span"),
            price = (record.offer_type == "buying" ? String(new BigNumber(1).dividedBy(new BigNumber(record.price).toPrecision(15)).toFixed(7)) : record.price),
            priceCss = (record.offer_type == "buying" ? 'text-primary font-weight-bold' : 'text-secondary font-weight-bold');

        priceSpan.setAttribute("class", priceCss);
        priceSpan.append(document.createTextNode(price));

        descriptionSpan.append(actorA);
        descriptionSpan.append(document.createTextNode(" " + action + " " + amount + " "));
        descriptionSpan.append(objectA);
        descriptionSpan.append(document.createTextNode(" at a price of "));
        descriptionSpan.append(priceSpan);
        descriptionSpan.append(document.createTextNode(" XLM"));
        break;
      case "follow":
        // Following user activity
        // e.x.: <span><a href="" class="text-dark font-weight-bold">@mikey.rf</a> started following <a href="" class="text-dark font-weight-bold">@feld27</a></span>
        featherIcon = "activity";

        objectA.append(document.createTextNode("@" + record.object_username));

        descriptionSpan.append(actorA);
        descriptionSpan.append(document.createTextNode(" started following "));
        descriptionSpan.append(objectA);
        break;
      case "trust":
        // Trusting asset
        // e.x.: <span><a href="" class="text-dark font-weight-bold">@mikey.rf</a> trusted <a href="" class="text-dark font-weight-bold">MOBI</a></span>
        featherIcon = "shield";

        objectA.append(document.createTextNode(record.object_code));

        descriptionSpan.append(actorA);
        descriptionSpan.append(document.createTextNode(" trusted "));
        descriptionSpan.append(objectA);
        break;
      case "post":
        // Posting message to timeline
        // e.x.: <span><a href="" class="text-dark font-weight-bold">@mikey.rf</a> posted</span>
        featherIcon = "edit-2";
        descriptionSpan.append(actorA);
        descriptionSpan.append(document.createTextNode(" posted"));
        break;
      case "comment":
        // Commenting on activity in timeline
        // e.x.: <span><a href="" class="text-dark font-weight-bold">@mikey.rf</a> commented</span>
        featherIcon = "message-circle";
        descriptionSpan.append(actorA);
        descriptionSpan.append(document.createTextNode(" commented"));
        break;
    }

    // Add the feather icon to list item then return li
    featherIconSpan.setAttribute("data-feather", featherIcon);
    return li;
  }

  /** postForm submission to Nucleo **/
  // TODO: Instantiate a listener to verify item has been added to feed before redirecting
  $('#postForm').submit(function(event) {
    event.preventDefault();

    // Grab the public_key data from the form
    let successUrl = this.dataset.success;

    // Build the JSON data to be submitted
    var formData = {};
    $(this).serializeArray().forEach(function(obj) {
      formData[obj.name] = obj.value;
    });

    // Start Ladda animation for UI loading
    let laddaButton = Ladda.create($(this).find(":submit")[0]);
    laddaButton.start();

    // Submit it to Nucleo's create account endpoint
    // TODO: IMPLEMENT A LISTENER FOR SUCCESSFUL ADDITION TO FEED IF NOT ALREADY LISTENING: Use
    $.post(this.action, formData)
    .then(function(result) {
      // Then redirect to the user's profile page with successUrl
      // TODO: if (successUrl)
      window.location.href = successUrl;
    })
    .catch(function(error) {
      // Fail response gives form.errors. Make sure to show in error form
      // TODO: let modalHeader = $("#addStellarModalForm").find('.modal-body-header')[0];

      // Stop the button loading animation then display the error
      Ladda.stopAll();
      console.error('Something went wrong with Nucleo call', error);
      // TODO: displayError(modalHeader, error.message);
    });
  });
})();
