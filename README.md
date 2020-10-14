# Spentless. Collector

[![Build Status](https://travis-ci.com/SpentlessInc/spentless-collector.svg?branch=master)](https://travis-ci.com/SpentlessInc/spentless-collector)

# Description
The collector app created for receiving transaction information (as webhook) from monobank when a user makes any transaction operation. If a transaction event was received:
* save transaction to database
* send server event to front-end
* notify the user about transaction
* notify the user if the limit in the transaction category was exceeded.

# How to run?
Follow the instruction placed in [spentless-infrastructure](https://github.com/SpentlessInc/spentless-infrastructure).