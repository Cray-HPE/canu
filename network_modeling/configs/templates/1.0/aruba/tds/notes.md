


dm-spine-primary/secondary in tds/full

Needs variables: 


{{ variables.SUN_IP }}
{{ variables.MLAG_IP }} 
{{ variables.SUN_IP_GATEWAY }}

{% include 'common/ncn-m.lag.j2' %}
{% include 'common/ncn-w.lag.j2' %}
{% include 'common/ncn-s.lag.j2' %}
{% include 'common/uan.j2' %}
{% include 'tds/spine-to-leaf-bmc.lag.j2' %}
{% include 'common/spine-to-cdu.lag.j2' %}

<- needs new port config templates

should we rename: 

mlag-vip gamora-mlag-domain ip 192.168.255.242 /29 force

to: 

mlag-vip cray-mlag-domain ip 192.168.255.242 /29 force

?


dm-leaf

needs: 
 {{ variables.CAN_IP }}

{{ variables.MTN_NMN }}

{{ variables.MTN_HMN }}

{% include 'tds/leaf-bmc-to-spine.lag.j2' %}
{% include 'common/bmc.j2' %}

{% include 'common/ncn-m.lag.j2' %}
{% include 'common/ncn-w.lag.j2' %}
{% include 'common/ncn-s.lag.j2' %}
{% include 'common/uan.j2' %}
{% include 'tds/spine-to-leaf-bmc.lag.j2' %}
{% include 'common/spine-to-cdu.lag.j2' %}

<- needs  new port config templates

should we rename:

mlag-vip shandy
-mlag-domain ip 192.168.255.242 /29 force

to:

mlag-vip cray-mlag-domain ip 192.168.255.242 /29 force
