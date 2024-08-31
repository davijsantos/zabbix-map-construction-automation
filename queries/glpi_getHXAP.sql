SELECT
    p.name as PERIPHERAL,
    p.SERIAL,
    pl.endereoipfield as IPV4,
    psigla.name as SIGLASE,
    pse.name as SE,
    apdm.name as AP_DEVICE_MODE,
    p.entities_id as entidade
FROM
    glpi_peripherals as p
LEFT JOIN
    glpi_plugin_fields_peripheraldeviceconfigurations as pl ON pl.items_id = p.id
LEFT JOIN
    glpi_plugin_fields_apdevicemodefielddropdowns as apdm ON apdm.id = pl.plugin_fields_apdevicemodefielddropdowns_id
LEFT JOIN
    glpi_plugin_fields_siglasedropdownfielddropdowns as psigla ON psigla.id = pl.plugin_fields_siglasedropdownfielddropdowns_id
LEFT JOIN
    glpi_plugin_fields_sedropdownfielddropdowns as pse ON pse.id = pl.plugin_fields_sedropdownfielddropdowns_id
WHERE
    p.is_deleted != 1
    AND p.peripheraltypes_id = '2'
    AND p.states_id not in ('172');