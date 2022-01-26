# ha-pallone-sensor

⚽ A sensor that provides next match date sensor for you favourite footaball team in home assistant. ⚽

The sensor created will have a default name PALLONE. You can change optionally the name into the integration.

The sensor state will be the date UTC of the match. If no match for the team id provided will be found the state will have a state of "OFF"

Within the sensor you will found attributes about the match:

| ATTRIBUTE NAME | DESCRIPTION                                                                                       |
| -------------- | ------------------------------------------------------------------------------------------------- |
| home_team_name | home team name                                                                                    |
| home_team_logo | logo for the home team                                                                            |
| away_team_logo | logo for the away team                                                                            |
| away_team_name | away team name                                                                                    |
| match_day      | the date utc of the match                                                                         |
| venue          | stadium name                                                                                      |
| venue location | the location where the match will play                                                            |
| referee        | the name of the referee                                                                           |
| league         | the name league of the match (example: serie A, Coppa Italia, Europe League                       |
| league_logo    | the logo for the league of the match                                                              |
| league_round   | the round for the league                                                                          |
| today_match    | boolean. If the match will be today or not (can be used in some automations to send alerts etc... |
| last_update    | last time sensor was updated                                                                      |

This is based on the free stack of api-sports.io apis for football.

## installation

### manually

Download this repo and copy the content of the pallone/custom_component folder under your_installation/custom_components/pallone/...

## configuration

After the installation and the correct reboot of HA go to configuration->devices&settings->integrations and add PALLONE. use the following table to find your favoruite team id(please request new leagues if interested).
You can set the name of the sensor at your choice (or leave as PALLONE) and you have to grab you api key by registering here : https://dashboard.api-football.com/register

once registered grab your api key from the left menu -> account -> my access (top right API-KEY).

<details>
  <summary>🇮🇹 ITALIAN SERIE A IDs List</summary>
  
  | TEAM ID  | TEAM |
  | --- | ------|
  | 487 | Lazio |
  | 488 | Sassuolo |
  | 489 | AC Milan |
  | 490 | Cagliari |
  | 492 | Napoli |
  | 494 | Udinese |
  | 495 | Genoa |
  | 496 | Juventus |
  | 497 | AS Roma |
  | 498 | Sampdoria |
  | 499 | Atalanta |
  | 500 | Bologna |
  | 502 | Fiorentina |
  | 503 | Torino |
  | 504 | Verona |
  | 505 | Inter |
  | 511 | Empoli |
  | 514 | Salernitana |
  | 515 | Spezia |
  | 517 | Venezia |
</details>
<details>
  <summary>🇬🇧 ENGLISH PREMIER LEAGUE IDs List</summary>
  
  | TEAM ID  | TEAM |
  | --- | ------|
  | 33 | Manchester United |
  | 34 | Newcastle |
  | 38 | Watford |
  | 39 | Wolves |
  | 40 | Liverpool |
  | 41 | Southampton |
  | 42 | Arsenal |
  | 44 | Burnley |
  | 45 | Everton |
  | 46 | Leicester |
  | 47 | Tottenham |
  | 48 | West Ham |
  | 49 | Chelsea |
  | 50 | Manchester City |
  | 51 | Brighton |
  | 52 | Crystal Palace |
  | 55 | Brentford |
  | 63 | Leeds |
  | 66 | Aston Villa |
  | 71 | Norwich |
</details>
