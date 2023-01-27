# Distributed leader election test in python

[Leader Election Wikipedia](https://en.wikipedia.org/wiki/Leader_election)

Attempting to write a distributed system that elects a leader, keeps track of which host_ID's are at which host. Recalculate when certain hosts go down or change.

TODO:
- [ ] Add alive checks
- [ ] Propagate changes across hosts with interaction (currently required to interact with middle host)
- [ ] Catch exit flask thread. Current main catch event is not hit.
- [ ] Other bits :)