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
    hgrp.NAME IN ('.COPEL1/HEXING AP','.COPEL2/HEXING AP')
    AND t.expression = CONCAT('{', f.functionid, '}=0') /* Ex: {21039564:availability.status.last()}=0 */
    /* AND h.HOST REGEXP '^[A-Z]{3,3}-[A-Z]-A-[0-9]{3,3}$'*/
    /* AND h.STATUS = 0 */
    /* AND i.STATUS = 0 */
    /* AND t.STATUS = 0 */
    /* AND t.STATE = 0 */
GROUP BY
    h.NAME
ORDER BY
    h.NAME ASC;