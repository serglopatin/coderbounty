"use strict";

var bountyButton, bountyButtonId, hasBountyButton, selectMenu;

bountyButtonId = "cbe-bounty-button";
selectMenu = document.getElementsByClassName("js-select-menu")[0];
hasBountyButton = selectMenu.querySelector("#" + bountyButtonId) !== null;

if (!hasBountyButton) {
    bountyButton = document.createElement("button");
    bountyButton.innerHTML = "Add a Bounty";
    bountyButton.setAttribute("id", bountyButtonId);
    bountyButton.className = "btn";
    bountyButton.onclick = function bountyButtonClick() {
        window.location = "http://coderbounty.com/post/?url=" + location.protocol + "//" + location.host+location.pathname;
    };
    bountyButton.style.background = "#9A8C76";
    bountyButton.style.color = "#FFF";

    selectMenu.appendChild(bountyButton);
}
