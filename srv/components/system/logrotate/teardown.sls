# Log rotate teardown start
# logrotate.d
Remove logrotate directory:
  file.absent:
    - name: /etc/logrotate.d

# general settings
Remove generic logrotate config:
  file.absent:
    - name: /etc/logrotate.conf
    - source: salt://components/system/files/etc/logrotate.conf

# Remove logrotate
Remove logrotate package:
  pkg.installed:
    - name: logrotate