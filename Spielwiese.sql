SELECT
    `tblGesamt`.`ID` AS `ID`,
    `tblUserIDundName`.`Gruppe` AS `Gruppe`,
    `tblUserIDundName`.`Orga_ID` AS `Orga_ID`,
    `tblGesamt`.`UserID + Name_ID` AS `UserID + Name_ID`,
    `tblGesamt`.`TF` AS `TF`,
    `tblGesamt`.`TF Beschreibung` AS `TF Beschreibung`,
    `tblGesamt`.`Enthalten in AF` AS `Enthalten IN AF`,
    `tblGesamt`.`Modell` AS `Modell`,
    `tblGesamt`.`Plattform_ID` AS `Plattform_ID`,
    `tblGesamt`.`GF` AS `GF`,
    `tblGesamt`.`GF Beschreibung` AS `GF Beschreibung`,
    `tblGesamt`.`gelöscht` AS `gelöscht`,
    `tblGesamt`.`löschdatum` AS `löschdatum`,
    `tblGesamt`.`AF Gültig ab` AS `AF Gültig ab`,
    `tblGesamt`.`AF Gültig bis` AS `AF Gültig bis`,
    `tblGesamt`.`Direct Connect` AS `Direct Connect`,
    `tblGesamt`.`Höchste Kritikalität TF in AF` AS `Höchste Kritikalität TF IN AF`,
    `tblGesamt`.`AF Zuweisungsdatum` AS `AF Zuweisungsdatum`,
    `tbl_RACF_Gruppen`.`Test` AS `Test`,
    `tbl_RACF_Gruppen`.`Produktion` AS `Produktion`,
    `tbl_RACF_Gruppen`.`Readonly` AS `Readonly`,
    `tblGesamt`.`TF Kritikalität` AS `TF Kritikalität`,
    `tblGesamt`.`TF Eigentümer Org` AS `TF Eigentümer Org`,
    `tblUserIDundName`.`ZI-Organisation` AS `ZI-Organisation`,
    `tblGesamt`.`Datum` AS `Datum`,
    `tblGesamt`.`gefunden` AS `gefunden`,
    `tblGesamt`.`wiedergefunden` AS `wiedergefunden`,
    `tblGesamt`.`geändert` AS `geändert`,
    `tblGesamt`.`NeueAF` AS `NeueAF`,
    `tblUserIDundName`.`UserID` AS `UserID`,
    `tblUserIDundName`.`Name` AS `Name`,
    `tblGesamt`.`VIP Kennzeichen` AS `VIP Kennzeichen`,
    `tblGesamt`.`Zufallsgenerator` AS `Zufallsgenerator`
FROM
    (
        `tblÜbersichtAF_GFs`
    JOIN(
            `tblPlattform`
        JOIN(
                (
                    (
                        `tblUserIDundName`
                    JOIN `tblGesamt` ON
                        (
                            (
                                (`tblUserIDundName`.`gelöscht` <> 1) AND(
                                    `tblUserIDundName`.`ID` = `tblGesamt`.`UserID + Name_ID`
                                )
                            )
                        )
                    )
                LEFT JOIN `tbl_RACF_Gruppen` ON
                    (
                        (
                            `tbl_RACF_Gruppen`.`Group` = `tblGesamt`.`TF`
                        )
                    )
                )
            LEFT JOIN `tblOrga` ON
                (
                    (
                        `tblOrga`.`ID` = `tblUserIDundName`.`Orga_ID`
                    )
                )
            )
        ON
            (
                (
                    `tblPlattform`.`ID` = `tblGesamt`.`Plattform_ID`
                )
            )
        )
    ON
        (
            (
                `tblÜbersichtAF_GFs`.`ID` = `tblGesamt`.`Modell`
            )
        )
    )
    where
  	 `ZI-organisation` = 'AI-BA'
     	AND NOT `tblGesamt`.`gelöscht`
        AND NOT `tblUserIDundName`.`gelöscht`
	LIMIT 3





SELECT COUNT (`tblGesamt``.`id``)
FROM
    (
        `tblÜbersichtAF_GFs`
    JOIN(
            `tblPlattform`
        JOIN(
                (
                    (
                        `tblUserIDundName`
                    JOIN `tblGesamt` ON
                        (
                            (
                                (`tblUserIDundName`.`gelöscht` <> 1) AND(
                                    `tblUserIDundName`.`ID` = `tblGesamt`.`UserID + Name_ID`
                                )
                            )
                        )
                    )
                LEFT JOIN `tbl_RACF_Gruppen` ON
                    (
                        (
                            `tbl_RACF_Gruppen`.`Group` = `tblGesamt`.`TF`
                        )
                    )
                )
            LEFT JOIN `tblOrga` ON
                (
                    (
                        `tblOrga`.`ID` = `tblUserIDundName`.`Orga_ID`
                    )
                )
            )
        ON
            (
                (
                    `tblPlattform`.`ID` = `tblGesamt`.`Plattform_ID`
                )
            )
        )
    ON
        (
            (
                `tblÜbersichtAF_GFs`.`ID` = `tblGesamt`.`Modell`
            )
        )
    )
    where
  	 `ZI-organisation` = 'AI-BA'
     	AND NOT `tblGesamt`.`gelöscht`
        AND NOT `tblUserIDundName`.`gelöscht`


SET global general_log = 1;
SET global log_output = 'table';
SET global general_log = 0;

SELECT * FROM `mysql`.`general_log` WHERE event_time  > (now() - INTERVAL 8 SECOND) AND `user_host` LIKE 'RechteFuzzi[RechteFuzzi]%' ORDER BY `event_time` DESC
SELECT * FROM `mysql`.`general_log` WHERE `user_host` LIKE 'RechteFuzzi[RechteFuzzi]%' ORDER BY `event_time` DESC
