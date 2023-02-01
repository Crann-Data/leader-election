# Distributed leader election test in python

[Leader Election Wikipedia](https://en.wikipedia.org/wiki/Leader_election)

Attempting to write a distributed system that elects a leader, keeps track of which host_ID's are at which host. Recalculate when certain hosts go down or change.

TODO:
- [x] Add alive checks
- [ ] Propagate changes across hosts without interaction (currently required to interact with middle host)
- [ ] Catch exit flask thread. Current main catch event is not hit.
- [ ] Other bits :)
- [x] MD5 hash host and port to map - checking if host already exists. Warning: Collisions possible in MD5 hashing
- [ ] Does not remove neighbour when host is brought down. I think this is because it's updating it's neighbours list from other hosts.