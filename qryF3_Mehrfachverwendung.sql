SELECT `tblGesamt`.`ID` AS `id`,
		`tblUserIDundName`.`UserID` AS `UserID`,
		`tblUserIDundName`.`Name` AS `Name`,
		`tblUserIDundName`.`Gruppe` AS `gruppe`,
		`tblOrga`.`Intern - extern` AS `team`,
		`tblGesamt`.`TF` AS `TF`,
		`tblGesamt`.`TF Beschreibung` AS `TF Beschreibung`,
		`tblGesamt`.`Enthalten in AF` AS `Enthalten IN AF`,
		`tblÜbersichtAF_GFs`.`Name AF Neu` AS `afneu`,
		`tblÜbersichtAF_GFs`.`Name GF Neu` AS `gfneu`,
		`tblPlattform`.`TF Technische Plattform` AS `plattform`,
		`tblGesamt`.`GF` AS `GF`,
		`tblGesamt`.`GF Beschreibung` AS `GF Beschreibung`,
		`tblUserIDundName`.`Orga_ID` AS `Orga_ID`,
		`tblGesamt`.`UserID + Name_ID` AS `UserIDundName_ID`,
		`tblGesamt`.`Modell` AS `Modell`,
		`tblGesamt`.`Plattform_ID` AS `Plattform_ID`,
		`tblGesamt`.`gelöscht` AS `geloescht`,
		`tblGesamt`.`löschdatum` AS `loeschdatum`,
		`tblGesamt`.`AF Gültig ab` AS `AF Gueltig ab`,
		`tblGesamt`.`AF Gültig bis` AS `AF Gueltig bis`,
		`tblGesamt`.`Direct Connect` AS `Direct Connect`,
		`tblGesamt`.`Höchste Kritikalität TF in AF` AS `Hoechste Kritikalitaet TF IN AF`,
		`tblGesamt`.`AF Zuweisungsdatum` AS `AF Zuweisungsdatum`,
		`tbl_RACF_Gruppen`.`Test` AS `Test`,
		`tbl_RACF_Gruppen`.`Produktion` AS `Produktion`,
		`tbl_RACF_Gruppen`.`Readonly` AS `Readonly`,
		`tblGesamt`.`TF Kritikalität` AS `TF_Kritikalitaet`,
		`tblGesamt`.`TF Eigentümer Org` AS `TF_Eigentuemer Org`,
		`tblUserIDundName`.`ZI-Organisation` AS `ZI_Organisation`,
		`tblGesamt`.`VIP Kennzeichen` AS `VIP`,
		`tblGesamt`.`Zufallsgenerator` AS `Zufallsgenerator`,
		`tblGesamt`.`Datum` AS `Datum`,
		`tblGesamt`.`gefunden` AS `gefunden`,
		`tblGesamt`.`wiedergefunden` AS `wiedergefunden`,
		`tblGesamt`.`geändert` AS `geaendert`,
		`tblGesamt`.`NeueAF` AS `NeueAF`

		FROM (`tblÜbersichtAF_GFs`
			JOIN (`tblPlattform`
				JOIN (((`tblUserIDundName`
					JOIN `tblGesamt`
					on(((`tblUserIDundName`.`gelöscht` <> 1) AND (`tblUserIDundName`.`ID` = `tblGesamt`.`UserID + Name_ID`))))
					LEFT JOIN `tbl_RACF_Gruppen`
					on((`tbl_RACF_Gruppen`.`Group` = `tblGesamt`.`TF`)))
						LEFT JOIN `tblOrga`
						on((`tblOrga`.`ID` = `tblUserIDundName`.`Orga_ID`)))
				on((`tblPlattform`.`ID` = `tblGesamt`.`Plattform_ID`)))
			on((`tblÜbersichtAF_GFs`.`ID` = `tblGesamt`.`Modell`)))
		WHERE NOT `tblUserIDundName`.`gelöscht`
		AND NOT tblGesamt.`gelöscht`

-- ToDo Das Team fehlt noich in der Liste (Orga.`Intern - extern`
-- 533819 in tblGesamt