WITH tickets as (
	SELECT t.status, t.id, CASE
			WHEN t.status in (1,2,3,4) THEN gtdp.id
			ELSE "-"
		END as "tipo_de_pendencia", git.items_id
    FROM glpi_peripherals p
    LEFT JOIN
		glpi_items_tickets git ON git.items_id = p.id AND git.itemtype = "Peripheral"
	LEFT JOIN glpi_tickets t ON t.id = git.tickets_id
    LEFT JOIN
		glpi_plugin_fields_ticketothercategories gtoc ON gtoc.items_id = t.id
	LEFT JOIN
		glpi_plugin_fields_tipodependenciafielddropdowns gtdp ON gtdp.id = gtoc.plugin_fields_tipodependenciafielddropdowns_id
	LEFT JOIN
		glpi_plugin_fields_ticketsolutions gts ON gts.items_id = t.id
	LEFT JOIN
		glpi_plugin_fields_otimizacaocronogramafielddropdowns goc ON gts.plugin_fields_otimizacaocronogramafielddropdowns_id = goc.id
    INNER JOIN (
        SELECT git.items_id,MAX(t.id) as max_id
        FROM glpi_tickets t
        LEFT JOIN glpi_items_tickets git ON git.tickets_id = t.id AND git.itemtype = "Peripheral"
        LEFT JOIN glpi_peripherals p ON p.id = git.items_id
        WHERE
        t.is_deleted = 0
        AND t.status in (1,2,3,4,5)
        GROUP BY git.items_id
        ORDER BY t.status ASC, t.id DESC
    ) sub ON t.id = sub.max_id AND p.id = sub.items_id
	WHERE
        t.is_deleted = 0
    AND t.status in (1,2,3,4,5)
	GROUP BY git.items_id
	ORDER BY t.status ASC, t.id DESC
)

SELECT
    p.NAME as PERIPHERAL,
    p.SERIAL,
    pl.ENDEREOIPFIELD as IPV4,
    pdm.NAME as DEVICEMODE,  /* store-and-forward, remote, access-point */
    pte.NAME as EQUIPMENTTYPE /* GE-B2B, GE+AP, GE-B2B+AP, .etc */,
    pt.NAME as DEVICETYPE,  /* ECR, MCR OR P70 */
    pl.NOMEDOPRXIMOEQUIPAMENTOFIELD as NEXTDEVICE,
    CASE
        WHEN pnid.NAME LIKE '%-P7-%' THEN "510"
        ELSE pnid.NAME
    END AS NIC_ID,
    pgwid.NAME as GATEWAY_ID,
    pl.NOMEDAREDEFIELD as NETWORKNAME,
    poi.NAME as INSTALLATIONORDER,
    CASE
        WHEN pl.BTWOBFIELD = '1' THEN "YES"
        ELSE "NO"
    END as B2B,
    pl.IDBTWOBFIELD as IDBTWOB,
    pl.IDAPFIELD as IDAP,
    pl.IDDAFIELD as IDDA,
    pse.NAME as SE,
    psigla.NAME as SIGLASE,
    p.entities_id as "entidade",
	ifnull(t.status,"-") as "status_ticket",
    ifnull(t.id,"-") as "ticket_id",
	t.tipo_de_pendencia as "tipo_de_pendencia"
FROM
    glpi_peripherals as p
LEFT JOIN
    glpi_plugin_fields_peripheraldeviceconfigurations as pl ON pl.ITEMS_ID = p.ID
LEFT JOIN
    glpi_states as pstate ON pstate.ID = p.STATES_ID
LEFT JOIN
    glpi_plugin_fields_devicemodedropdownfielddropdowns as pdm ON pdm.ID = pl.PLUGIN_FIELDS_DEVICEMODEDROPDOWNFIELDDROPDOWNS_ID
LEFT JOIN
    glpi_plugin_fields_realdevicetypefielddropdowns as pte ON pte.ID = pl.PLUGIN_FIELDS_REALDEVICETYPEFIELDDROPDOWNS_ID
LEFT JOIN
    glpi_plugin_fields_devicetypedropdownfielddropdowns as pt ON pt.ID = pl.PLUGIN_FIELDS_DEVICETYPEDROPDOWNFIELDDROPDOWNS_ID
LEFT JOIN
    glpi_plugin_fields_niciddropdownfielddropdowns as pnid ON pnid.ID = pl.PLUGIN_FIELDS_NICIDDROPDOWNFIELDDROPDOWNS_ID
LEFT JOIN
    glpi_plugin_fields_gwiddropdownfielddropdowns as pgwid ON pgwid.ID = pl.PLUGIN_FIELDS_GWIDDROPDOWNFIELDDROPDOWNS_ID
LEFT JOIN
    glpi_plugin_fields_installationorderdropdownfielddropdowns as poi ON poi.ID = pl.PLUGIN_FIELDS_INSTALLATIONORDERDROPDOWNFIELDDROPDOWNS_ID
LEFT JOIN
    glpi_plugin_fields_siglasedropdownfielddropdowns as psigla ON psigla.ID = pl.PLUGIN_FIELDS_SIGLASEDROPDOWNFIELDDROPDOWNS_ID
LEFT JOIN
    glpi_plugin_fields_sedropdownfielddropdowns as pse ON pse.ID = pl.PLUGIN_FIELDS_SEDROPDOWNFIELDDROPDOWNS_ID
LEFT JOIN
	tickets t ON t.items_id = p.id
WHERE
    p.IS_DELETED != 1
    AND p.PERIPHERALTYPES_ID = '1'
    AND pstate.id not in ("172")
GROUP BY
	p.name;