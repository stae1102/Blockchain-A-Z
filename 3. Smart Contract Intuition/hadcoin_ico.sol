//SPDX-License-Identifier: MIT

// Hadcoins ICO

// Version of compiler
pragma solidity ^0.8.14;

contract Hadcoin_ico {

  // Introducing the maximum number of Hadcoins available for sale
  uint public max_hadcoins = 1_000_000;

  // Introducing the USD to Hadcoins conversion rate
  uint public usd_to_hadcoins = 1_000;

  // Introducing the total number of Hadcoins that have been bought by the investors
  uint public total_hadcoins_bought = 0;

  // Mapping from the investor address to tis equity in Hadcoins and USD
  mapping(address => uint) equity_hadcoins;
  mapping(address => uint) equity_usd;

}