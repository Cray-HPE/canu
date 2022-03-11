{#- edge_router #}


interface Vlan{{ variables.CHN_VLAN }}
   ip address {{ variables.CHN_IP }}/{{variables.CHN_PREFIX_LEN}}

ip routing

ip prefix-list HSN seq 10 permit {{ variables.CHN }}/{{ variables.CHN_PREFIX_LEN }} ge {{ variables.CHN_PREFIX_LEN }}
!
route-map HSN permit 5
   match ip address prefix-list HSN

router bgp {{ variables.SWITCH_ASN }}
   maximum-paths 32
   {%- for name, ip in variables.CHN_IPs.items() if "ncn-w" in name %}
   neighbor {{ ip }} remote-as {{ variables.CHN_ASN }}
   neighbor {{ ip }} transport connection-mode passive
   neighbor {{ ip }} route-map HSN in

{#- end edge_router #}