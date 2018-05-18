# Provisioning

This script uses Ansible to set up provisioning on the servers. The
following details are of interest to get things running:

1. Make sure that the folder `master-keys` contains a standard SSH
keypair to be installed in the Master machine. This will be set up so
that the master has passwordless SSH access to all the workers (and
itself, incidentally). 

2. Add the servers to the correct groups in `spark-ansible.inventory`
and state their correct IP numbers and host names.

3. Provision with `ansible-playbook -ispark-ansible.inventory
spark-playbook.yaml` (from a computer that has Ansible installed).

4. Add the correct *local* addresses to the workers in `spark-playbook.yaml`

Also, when launching the VMs, make sure to install Ansible by adding the
customisation script `setup.sh` in OpenStack.

The setup works as follows:
- The master launches the workers in a stand-alone cluster configuration.
- All nodes are set up to have their data in `/home/ubuntu/data`,
  mounted from an NFS share
- Python prerequisites are loaded and installed from
  `../requirements.txt`.
