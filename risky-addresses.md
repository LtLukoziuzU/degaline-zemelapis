# Risky Addresses for Geocoding

Addresses from `data/latest.xlsx` (2026-04-09, 713 stations) that may geocode poorly.
These fall into two categories:

**Pure village names** — no street or number, will resolve to village centre at best.
**Village + plot/cadastral number** — the number is not a street number; Nominatim won't understand it.

After geocoding, cross-check these against their map pins to verify placement is sensible.
Any that land in the wrong location should be manually deleted from `geocache.json` to force a retry,
or accepted as `source: "municipality"` fallbacks.

## Address list (48 entries)

| Address | Municipality |
|---|---|
| Aleksandravo k. | Marijampolės sav. |
| Alytaus k. | Alytaus r. sav. |
| Bajorų k. | Anykščių r. sav. |
| Biruliškių k. | Kauno r. sav. |
| Brazdigalos k. 1 | Pasvalio r. sav. |
| Bukiškio k. Ukmergės g.437 | Vilniaus r. sav. |
| Bučių k. | Šilalės r. sav. |
| Dumblės k. | Šalčininkų r. sav. |
| Gineikių k. | Šilalės r. sav. |
| Grigaliūnų k. 11 | Prienų r. sav. |
| Griškabūdis | Šakių r. sav. |
| Gustaičių k. | Prienų r. sav. |
| Jaučiakių k. | Kauno r. sav. |
| Juodalaukių k. 2 | Zarasų r. sav. |
| Kalnujų k. 1 | Raseinių r. sav. |
| Kalnuotės 1 k. | Vilniaus r. sav. |
| Kaniukų k. | Alytaus r. sav. |
| Kantališkių k. | Marijampolės sav. |
| Kerelių k. 1A | Kupiškio r. sav. |
| Kretingsodžio k. | Kretingos r. sav. |
| Kuodaičių k. | Šilalės r. sav. |
| Kuosiškių k. 4 | Pakruojo r. sav. |
| Likiškėlių k. | Alytaus r. sav. |
| Margavos k. | Kauno r. sav. |
| Medelyno g.126 Kalotės k. | Klaipėdos r. sav. |
| Nekrūnų k. 1 | Lazdijų r. sav. |
| Pasiekų k. | Marijampolės sav. |
| Pietarių k. Kauno g. 164 | Marijampolės sav. |
| Pikelių k. 1 | Raseinių r. sav. |
| Pikelių k. 6 | Raseinių r. sav. |
| Pikelių k. 8 | Raseinių r. sav. |
| Radikių k. | Joniškio r. sav. |
| Raščių k. 1A | Raseinių r. sav. |
| Ruoščių k. 1 | Kėdainių r. sav. |
| Sausalaukės k. 2 | Anykščių r. sav. |
| Sausių g.2 Sausių k.. | Trakų r. sav. |
| Skabeikių k. 4 | Akmenės r. sav. |
| Smėlinkos k. | Molėtų r. sav. |
| Tartoko k. | Šalčininkų r. sav. |
| Užubalių k. Senasis Ukmergės kelias 4 | Vilniaus r. sav. |
| Užuovėjos k. | Radviliškio r. sav. |
| Valantiškio k. | Biržų r. sav. |
| Veiverių k. | Prienų r. sav. |
| Vejukų k. 5 | Raseinių r. sav. |
| Vilimiškės k. | Kretingos r. sav. |
| Vilkaraisčio k. | Vilniaus r. sav. |
| Ąžuolų Būdos k. | Kazlų Rūdos sav. |
| Žiežmarių k. | Kaišiadorių r. sav. |

## Notes

- `Griškabūdis` — single town name, no suffix; likely fine but worth checking.
- `Bukiškio k. Ukmergės g.437`, `Pietarių k. Kauno g. 164`, `Medelyno g.126 Kalotės k.`,
  `Užubalių k. Senasis Ukmergės kelias 4` — have street info but unusual formatting
  (village name first); Nominatim may or may not parse them correctly.
- `Sausių g.2 Sausių k..` — double trailing dot, likely a typo in ENA's data.
- For any that fail or land in the wrong place: delete the entry from `geocache.json`
  and add municipality name manually as a coordinate hint, or accept the municipality
  centre fallback.
