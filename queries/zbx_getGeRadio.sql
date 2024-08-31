SELECT DISTINCT
    h.HOST,
    h.NAME,
    h.DESCRIPTION,
    CONVERT(h.HOSTID, CHAR) AS HOSTID,
    CONVERT(f.TRIGGERID, CHAR) AS PING_TRIGGER_ID,
    iface.IP AS IPV4,
    CASE
        WHEN hinv.HOST_ROUTER NOT REGEXP '^[A-Z]{3,3}-' THEN NULL
        ELSE hinv.HOST_ROUTER
    END AS HOST_ROUTER
FROM
    hosts h
INNER JOIN
    items i ON i.HOSTID = h.HOSTID
INNER JOIN
    functions f ON i.ITEMID = f.ITEMID
INNER JOIN
    triggers t ON ( f.TRIGGERID = t.TRIGGERID ) 
INNER JOIN 
    hosts_groups hg ON h.HOSTID = hg.HOSTID
INNER JOIN
    hstgrp hgrp ON hg.GROUPID = hgrp.GROUPID
INNER JOIN
    interface iface ON iface.HOSTID = h.HOSTID
INNER JOIN
    host_inventory hinv ON hinv.HOSTID = h.HOSTID
WHERE
    hgrp.NAME IN ('.COPEL1/GE','.COPEL2/GE')
    AND t.expression = CONCAT('{', f.functionid, '}=0')
GROUP BY
    h.NAME
ORDER BY
    h.NAME ASC;