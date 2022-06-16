# Design
There is a single client which can run multiple services which it uses to participate.

### Folder Layout
(Not sure if the server folder will still exist or if it will get integrated into the services section)

- The main client to run is the Client_main.py
- Services folder to hold modular addons 
- Data folder to hold data
  - Archived/held posts
  - Misc data
    - login info
    - caches
    - permission tokens

##### Files of importance
- data/anchor
  - Location verification
  - What mode to use the client in
- data/user/tokens
  - Stores access information for requesting files
- data/user/gates
  - cache of previous network access points
- Services
  - Holds all the different modules I may care about
  - Some actually run their own services, others just support
    - Consider moving the libs to their own directory
  - Nothing here is supposed to be run directly


##### There are a few servers that the client can host/run
- Gate Server
  - Is the entry point into the network
  - Acts as a simple cache of all relevant nodes a new client should care about
  - Shares a list of gates and directors to the client
  - Its cache get updated through the director
  - We assume there will be lots of sudden joining/leaving network
- Director server
  - Organizes topography of normal clients
  - Sets up client feed
    - Send feed info (metadata + location + auth)
  - Inform hoster about incoming request (includes auth)