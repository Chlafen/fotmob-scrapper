import api_service
import pandas as pd

from api_types import MatchDetails
from typing import List

from processing import export_data, filter_women_leagues, preprocess_data


async def main():
    all_leagues = await api_service.get_all_leagues_by_country()
    mens_leagues = filter_women_leagues(all_leagues)
    all_matches_details = []

    for league in mens_leagues:
        try:
            print("Getting league details for League: ", league.id)
            seasons = await api_service.get_all_available_seasons(league.id)
            print("  Found ", seasons, " Seasons")
            for season in seasons:
                try:
                    league_season = await api_service.get_league_by_id_season(league.id, league.ccode, season)
                    if league_season is None:
                        continue

                    first_unplayed_match_idx = -1

                    if league_season.matches.firstUnplayedMatch is not None:
                        first_unplayed_match_idx = league_season.matches.firstUnplayedMatch.firstUnplayedMatchIndex

                    print("Getting match details for League: ",
                          league_season.details.name)
                    print("  Found ", first_unplayed_match_idx, " Matches")

                    # get all played matches
                    for match in league_season.matches.allMatches[:first_unplayed_match_idx]:
                        try:
                            match_details = await api_service.get_match_details_by_id(match.id, season)
                            if (match_details is not None):
                                match_details.ccode = league_season.details.ccode
                                all_matches_details.append(match_details)
                        except Exception as e:
                            print("Error: ", e)
                except Exception as e:
                    print("Error: ", e)

        except Exception as e:
            print("Error: ", e)
            # continue with the next league

    print('Total', len(all_matches_details), 'matches found')

    export_data(all_matches_details)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
