# Distributed leader election test in python


Attempting to write a distributed system that elects a leader, keeps track of which host_ID's are at which host. Recalculate when certain hosts go down or change.

TODO:
- [ ] Add alive checks
- [ ] Propagate changes across hosts with interaction (currently required to interact with middle host)
- [ ] Other bits :)