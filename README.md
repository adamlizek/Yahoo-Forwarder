Now that Yahoo has decided to charge $1/Year per Forwarded Yahoo account, mass-forwarding yahoo emails is no longer viable for raffle entries.
Therefore I decided to refactor some of the old code and store it public on my GitHub.

No external Python Libraries are necessary.
Copy and Paste proxies into data/proxies/proxies.txt one per line in ip:port:user:pass format
Copy and Paste yahoo accounts into data/yahoo/yahoo_accounts.txt one per line in email:password format

Place your corresponding Chromedrvier from https://chromedriver.chromium.org/downloads into data/driver
You can fill various settings in the main program window and have it log to a Discord Webhook if desired. 

Not sure if it still works, but enjoy!