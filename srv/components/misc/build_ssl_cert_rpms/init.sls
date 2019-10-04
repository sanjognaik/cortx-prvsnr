{% set node = grains['id'] %}

{% if salt["pillar.get"]('cluster:{0}:is_primary'.format(node), false) %}

include:
  - components.misc.build_ssl_cert_rpms.install
  - components.misc.build_ssl_cert_rpms.prepare
  - components.misc.build_ssl_cert_rpms.config
  - components.misc.build_ssl_cert_rpms.housekeeping
  - components.misc.build_ssl_cert_rpms.sanity_check

{% else %}

# Fetch fqdn of primary node
{% for node_id in pillar['cluster']['node_list'] %}
  {% if salt['pillar.get']('cluster:{0}:is_primary'.format(node_id), None) %}

Copy certs from primary:
  cmd.run:
    # TODO safer way to pass known_hosts check, http://gitlab.mero.colo.seagate.com/eos/provisioner/ees-prvsnr/issues/15
    - name: scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {{ pillar['cluster'][node_id]['fqdn'] }}:/opt/seagate/stx-s3-*.rpm /opt/seagate

  {% endif %}
{% endfor %}
{% endif %}