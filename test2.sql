SELECT anon_1.season AS season,
    sum(anon_1.matches) AS matche s,
    CAST(sum(anon_1.losses) AS VARCHAR) || :param_1 || CAST(su m(anon_1.wins) AS VARCHAR) AS w_l,
    max(anon_1.opp_high_score) AS high_score,
    min(anon_1.opp_low_score) AS low_score,
    sum(a non_1.opp_wickets) AS wickets,
    sum(anon_1.opp_fours) AS fours,
    sum(anon_1.opp_sixes) AS sixes,
    round(
        (sum(anon_1.opp_runs) * :sum_1) / CAST(
            sum(anon_1.opp_legal_deliveries_faced) AS N UMERIC
        ),
        :round_1
    ) AS run_rate
FROM (
        SELECT matches.season AS season,
            matches.team1 AS team,
            count(*) AS matches,
            :param_2 AS innings,
            max(
                lpad(
                    matches.m _team1_score || :m_team1_score_1 || lpad(
                        CAST(matches.team2 A S VARCHAR),
                        :lpad_1,
                        :lpad_2
                    ),
                    :lpad_3,
                    :lpad_4
                )
            ) AS high_sco re,
            min(
                CASE
                    WHEN (
                        matches.team_won IS NOT NULL
                        AND matches.d ls != :dls_1
                        AND matches.overs_reduced != :overs_reduced_1
                    ) T HEN lpad(
                        matches.m_team1_score || :m_team1_score_2 || lpad(
                            CA ST(matches.team2 AS VARCHAR),
                            :lpad_5,
                            :lpad_6
                        ),
                        :lpad_7,
                        :lp ad_8
                    )
                    ELSE :param_3
                END
            ) AS low_score,
            sum(matches.team1_scor e) AS runs,
            sum(matches.team1_fours) AS fours,
            sum(matches.te am1_sixes) AS sixes,
            sum(matches.team1_legal_deliveries_faced) AS legal_deliveries_faced,
            sum(matches.team1_wickets) AS wi ckets,
            max(
                lpad(
                    matches.m_team2_score || :m_team2_score_1 || lpad(
                        CAST(matches.team1 AS VARCHAR),
                        :lpad_9,
                        :lpad_10
                    ),
                    :lpa d_11,
                    :lpad_12
                )
            ) AS opp_high_score,
            min(
                CASE
                    WHEN (
                        matches.te am_won IS NOT NULL
                        AND matches.dls != :dls_2
                        AND matches.over s_reduced != :overs_reduced_2
                    ) THEN lpad(
                        matches.m_team2_scor e || :m_team2_score_2 || lpad(
                            CAST(matches.team1 AS VARCHAR),
                            :lpad_13,
                            :lpad_14
                        ),
                        :lpad_15,
                        :lpad_16
                    )
                    ELSE :param_4
                END
            ) AS opp_low_score,
            sum(matches.team2_score) AS opp_runs,
            sum(m atches.team2_fours) AS opp_fours,
            sum(matches.team2_sixes) AS opp_sixes,
            sum(matches.team2_legal_deliveries_faced) AS opp_ legal_deliveries_faced,
            sum(matches.team2_wickets) AS opp_wic kets,
            sum(
                CASE
                    WHEN (matches.team_won = matches.team1) THEN: param_5
                    ELSE :param_6
                END
            ) AS wins,
            sum(
                CASE
                    WHEN (matches.te am_won = matches.team2) THEN :param_7
                    ELSE :param_8
                END
            ) AS l osses
        FROM matches
        GROUP BY matches.season,
            matches.team1
        UNION
        SEL ECT matches.season AS season,
        matches.team2 AS team,
        count(*) AS matches,
        :param_9 AS innings,
        max(
            lpad(
                matches.m_team2_sc ore || :m_team2_score_3 || lpad(
                    CAST(matches.team1 AS VARCHAR),
                    :lpad_17,
                    :lpad_18
                ),
                :lpad_19,
                :lpad_20
            )
        ) AS high_score,
        m in(
            CASE
                WHEN (
                    matches.team_won IS NOT NULL
                    AND matches.dls != :dls_3
                    AND matches.overs_reduced != :overs_reduced_3
                ) THEN l pad(
                    matches.m_team2_score || :m_team2_score_4 || lpad(
                        CAST(ma tches.team1 AS VARCHAR),
                        :lpad_21,
                        :lpad_22
                    ),
                    :lpad_23,
                    :lpad _24
                )
                ELSE :param_10
            END
        ) AS low_score,
        sum(matches.team2_scor e) AS runs,
        sum(matches.team2_fours) AS fours,
        sum(matches.te am2_sixes) AS sixes,
        sum(matches.team2_legal_deliveries_faced) AS legal_deliveries_faced,
        sum(matches.team2_wickets) AS wi ckets,
        max(
            lpad(
                matches.m_team1_score || :m_team1_score_3 || lpad(
                    CAST(matches.team2 AS VARCHAR),
                    :lpad_25,
                    :lpad_26
                ),
                :lp ad_27,
                :lpad_28
            )
        ) AS opp_high_score,
        min(
            CASE
                WHEN (
                    matches.t eam_won IS NOT NULL
                    AND matches.dls != :dls_4
                    AND matches.ove rs_reduced != :overs_reduced_4
                ) THEN lpad(
                    matches.m_team1_sco re || :m_team1_score_4 || lpad(
                        CAST(matches.team2 AS VARCHAR),
                        :lpad_29,
                        :lpad_30
                    ),
                    :lpad_31,
                    :lpad_32
                )
                ELSE :param_11
            END
        ) AS opp_low_score,
        sum(matches.team1_score) AS opp_runs,
        sum (matches.team1_fours) AS opp_fours,
        sum(matches.team1_sixes) AS opp_sixes,
        sum(matches.team1_legal_deliveries_faced) AS op p_legal_deliveries_faced,
        sum(matches.team1_wickets) AS opp_w ickets,
        sum(
            CASE
                WHEN (matches.team_won = matches.team2) THEN :param_12
                ELSE :param_13
            END
        ) AS wins,
        sum(
            CASE
                WHEN (matche s.team_won = matches.team1) THEN :param_14
                ELSE :param_15
            END
        ) AS losses
        FROM matches
        GROUP BY matches.season,
            matches.team2
    ) AS anon_ 1
GROUP BY anon_1.season
ORDER BY season DESC