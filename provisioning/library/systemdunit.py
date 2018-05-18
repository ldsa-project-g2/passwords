"""
Install Systemd units using Ansible

Handles unit restarting and systemd daemon reloading when the unit changes.

Also stops the unit correctly when uninstalled

In your playbook put this file to library/systemdunit.py and make sure the
server has python-sh package installed

Example:

- name: Add example.service
  systemdunit:
    name: "example.service"
    state: present
    # Use "state: absent" to uninstall
    content: |
      [Unit]
      Description=Just my example service

      [Service]
      ExecStart=/usr/local/bin/example

      [Install]
      WantedBy=basic.target

Use the normal systemd module to start it and enable it on boot

- name: Enable valu-backup service
  systemd: name="example.service" state=started enabled=yes


"""
import sh
import os.path

from ansible.module_utils.basic import AnsibleModule

import logging

logger = logging.getLogger('systemd')
hdlr = logging.FileHandler('/tmp/ansible-systemdunit.log')
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)


ROOT = "/etc/systemd/system/"


def present(unit_path, name, content):
    changed = False

    if not os.path.exists(unit_path):
        with open(unit_path, "w") as f:
            f.write(content)
            changed = True
        logger.info("Created new")
    else:
        current = sh.cat(unit_path)
        if current.strip() != content.strip():
            with open(unit_path, "w") as f:
                f.write(content)
                changed = True
            logger.info("Content changed")

    is_running = False

    try:
        sh.systemctl("is-active", name)
        is_running = True
    except sh.ErrorReturnCode:
        pass

    if changed:
        sh.systemctl("daemon-reload")

    if is_running and changed:
        logger.info("Restarting because changed and is running")
        sh.systemctl("restart", name)

    return changed


def absent(unit_path, name):
    changed = False

    try:
        sh.systemctl("stop", name)
        changed = True
        logger.info("Stopped")
    except sh.ErrorReturnCode:
        pass

    if os.path.exists(unit_path):
        sh.rm(unit_path)
        sh.systemctl("daemon-reload")
        changed = True
        logger.info("Removed")

    return changed


def main():
    arg_spec = dict(
        name=dict(default=None),
        content=dict(default=""),
        state=dict(default='present', choices=['present', 'absent']),
    )
    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )

    name = module.params['name'].strip()
    content = module.params['content'].strip()
    state = module.params['state']
    changed = False
    unit_path = ROOT + name

    logger.info("Editing systemd unit " + name)

    if state == "present":
        changed = present(unit_path, name, content)
    elif state == "absent":
        changed = absent(unit_path, name)
    else:
        raise Exception("Unknown state param")

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()