SELECT
    p.name as peripheral,
    pstate.completename as status,
    psigla.name as siglase,
    pse.name as se,
    pl.gatewaybackhaulfield as "gateway_backhaul",
    pl.gatewayamifield as "gateway_ami",
    pl.gatewaydafield as "gateway_da",
    pl.vlanbackaulfield as "vlan_backhaul",
    pl.vlanamifield as "vlan_ami",
    pl.vlandafield as "vlan_da",
    p.entities_id as "entidade"
FROM
    glpi_peripherals as p
LEFT JOIN
    glpi_plugin_fields_peripheraldeviceconfigurations as pl ON pl.items_id = p.id
LEFT JOIN
    glpi_states as pstate ON pstate.id = p.states_id
LEFT JOIN
    glpi_plugin_fields_siglasedropdownfielddropdowns as psigla ON psigla.id = pl.plugin_fields_siglasedropdownfielddropdowns_id
LEFT JOIN
    glpi_plugin_fields_sedropdownfielddropdowns as pse ON pse.id = pl.plugin_fields_sedropdownfielddropdowns_id
WHERE
    p.peripheraltypes_id = '5'
    -- AND pstate.completename LIKE 'Instalacao > Instalado%'
    AND p.is_deleted != 1