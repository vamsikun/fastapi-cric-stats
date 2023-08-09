from utils.getSQLQuery import getWherePredicate


def getSQLForTeamSummaryUnion():
    sql = """
    select season,
        team1 as team,
        count(*) as matches,
        1 as innings,
        max(
            lpad(
                m_team1_score || '-' || lpad(CAST(team2 as text), 3, '0'),
                10,
                '0'
            )
        ) as high_score,
        min(
            CASE
                -- low_score is not considered when dls or overs_reduced happens or no_result
                WHEN team_won is not null
                and dls != 1
                and overs_reduced != 1 THEN lpad(
                    m_team1_score || '-' || lpad(CAST(team2 as text), 3, '0'),
                    10,
                    '0'
                )
                ELSE 'ffffff'
            END
        ) as low_score,
        SUM(team1_score) as runs,
        SUM(team1_fours) as fours,
        SUM(team1_sixes) as sixes,
        SUM(team1_legal_deliveries_faced) as legal_deliveries_faced,
        SUM(team1_wickets) as wickets,
        max(
            lpad(
                m_team2_score || '-' || lpad(CAST(team2 as text), 3, '0'),
                9,
                '0'
            )
        ) as opp_high_score,
        min(
            CASE
                -- low_score is not considered when dls or overs_reduced happens or no_result
                WHEN team_won is not null
                and dls != 1
                and overs_reduced != 1 THEN lpad(
                    m_team2_score || '-' || lpad(CAST(team2 as text), 3, '0'),
                    9,
                    '0'
                )
                ELSE 'ffffff'
            END
        ) as opp_low_score,
        SUM(team2_score) as opp_runs,
        SUM(team2_fours) as opp_fours,
        SUM(team2_sixes) as opp_sixes,
        SUM(team2_legal_deliveries_faced) as opp_legal_deliveries_faced,
        SUM(team2_wickets) as opp_wickets,
        SUM(
            CASE
                WHEN team_won = team1 THEN 1
                ELSE 0
            END
        ) AS wins,
        SUM(
            CASE
                WHEN team_won = team2 THEN 1
                ELSE 0
            END
        ) AS losses
    from matches
    group by season,
        team1
    UNION
    SELECT season,
        team2 as team,
        count(*) as matches,
        2 as innings,
        MAX(
            lpad(
                m_team2_score || '-' || lpad(CAST(team1 as text), 3, '0'),
                9,
                '0'
            )
        ) AS high_score,
        min(
            CASE
                -- low_score is not considered when dls or overs_reduced happens or no_result
                WHEN team_won is not null
                and dls != 1
                and overs_reduced != 1 THEN lpad(
                    m_team2_score || '-' || lpad(CAST(team1 as text), 3, '0'),
                    9,
                    '0'
                )
                ELSE 'ffffff'
            END
        ) as low_score,
        SUM(team2_score) as runs,
        SUM(team2_fours) as fours,
        SUM(team2_sixes) as sixes,
        SUM(team2_legal_deliveries_faced) as legal_deliveries_faced,
        SUM(team2_wickets) as wickets,
        MAX(
            lpad(
                m_team1_score || '-' || lpad(CAST(team1 as text), 3, '0'),
                9,
                '0'
            )
        ) AS opp_high_score,
        min(
            CASE
                -- low_score is not considered when dls or overs_reduced happens or no_result
                WHEN team_won is not null
                and dls != 1
                and overs_reduced != 1 THEN lpad(
                    m_team1_score || '-' || lpad(CAST(team1 as text), 3, '0'),
                    9,
                    '0'
                )
                ELSE 'ffffff'
            END
        ) as opp_low_score,
        SUM(team1_score) as opp_runs,
        SUM(team1_fours) as opp_fours,
        SUM(team1_sixes) as opp_sixes,
        SUM(team1_legal_deliveries_faced) as opp_legal_deliveries_faced,
        SUM(team1_wickets) as opp_wickets,
        SUM(
            CASE
                WHEN team_won = team2 THEN 1
                ELSE 0
            END
        ) AS wins,
        SUM(
            CASE
                WHEN team_won = team1 THEN 1
                ELSE 0
            END
        ) AS losses
    FROM matches
    GROUP BY season,
    team2
    """
    return sql


def getSQLForTeamSummary(season: str, team: int, teamType: str, innings: int | None):
    wherePredicate = getWherePredicate(team=team, innings=innings)
    sqlForUnion = getSQLForTeamSummaryUnion()

    if innings == None:
        defaultCols = " season as season, sum(matches) as matches,  "
        appendToExtraCols = ""
        if teamType == "opp":
            defaultCols += (
                " cast(sum(losses) as text) || '/' || cast(sum(wins) as text) as w_l, "
            )
            appendToExtraCols = "opp_"
        else:
            defaultCols += (
                " cast(sum(wins) as text) || '/' || cast(sum(losses) as text) as w_l, "
            )
        extraCols = f""" max({appendToExtraCols}high_score) as high_score,
                            min({appendToExtraCols}low_score) as low_score,
                            sum({appendToExtraCols}wickets) as wickets,
                            sum({appendToExtraCols}fours) as fours,
                            sum({appendToExtraCols}sixes) as sixes,
                            ROUND(CAST(sum({appendToExtraCols}runs)/sum({appendToExtraCols}legal_deliveries_faced)::float as numeric)*6,3) as run_rate """
        defaultCols += extraCols
        groupByPredicate = " GROUP BY season"

    else:
        defaultCols = " season as season, matches, "
        appendToExtraCols = ""
        if teamType == "opp":
            defaultCols += " cast(losses as text) || '/' || cast(wins as text) as w_l, "
            appendToExtraCols = "opp_"
        else:
            defaultCols += " cast(wins as text) || '/' || cast(losses as text) as w_l, "

        extraCols = f"""  {appendToExtraCols}high_score as high_score,
                            {appendToExtraCols}low_score as low_score,
                            {appendToExtraCols}wickets as wickets,
                            {appendToExtraCols}fours as fours,
                            {appendToExtraCols}sixes as sixes,
                            ROUND(CAST({appendToExtraCols}runs/{appendToExtraCols}legal_deliveries_faced::float as NUMERIC)*6,3) as run_rate """
        defaultCols += extraCols
        groupByPredicate = ""

    s = f"""select {defaultCols}
            FROM ({sqlForUnion}) AS t
            WHERE {wherePredicate}
            {groupByPredicate}
            ORDER BY season DESC
        """
    return s
