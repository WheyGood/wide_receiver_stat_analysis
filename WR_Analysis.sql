use WRAnalysis;

-- Check the Data
SELECT * 
FROM WRAnalysis..ADV_WR_Stats

SELECT * 
FROM WRAnalysis..Points_WR_HALF

--Test a Left Join between the tables
SELECT a.player, a.team, b.points
FROM WRAnalysis..ADV_WR_Stats a LEFT JOIN WRAnalysis..Points_WR_HALF b
ON a.player = b.player AND a.team = b.team

--Create Joined Table for Exporting
SELECT a.*, b.points, b.[average] INTO WRAnalysis..export_me 
FROM WRAnalysis..ADV_WR_Stats a LEFT JOIN WRAnalysis..Points_WR_HALF b
ON a.player = b.player AND a.team = b.team
WHERE b.points IS NOT NULL

-- Determining the points per target per WR
SELECT a.player, a.team, b.points, a.targets, 
CASE
	WHEN a.targets = 0 THEN NULL
	ELSE (b.points / a.targets)
END AS pointspertarget
FROM WRAnalysis..ADV_WR_Stats a LEFT JOIN WRAnalysis..Points_WR_HALF b
ON a.player = b.player AND a.team = b.team
ORDER BY points DESC

--Determine receptions per target
SELECT a.player, a.team, a.rec, a.targets, 
CASE
	WHEN a.targets = 0 THEN NULL
	ELSE (a.rec / a.targets)
END AS recpertarget
FROM WRAnalysis..ADV_WR_Stats a LEFT JOIN WRAnalysis..Points_WR_HALF b
ON a.player = b.player AND a.team = b.team
WHERE a.targets > 10
ORDER BY recpertarget DESC 

--Show Team's total targets for Wrs and AveragePoints for their players
SELECT  a.team,
		COUNT(a.player) AS totalwrs, 
		SUM(targets) AS totalteamtargets, 
		AVG(b.points) / MAX(b.games) AS averagewrpointspergame		
FROM WRAnalysis..ADV_WR_Stats a LEFT JOIN WRAnalysis..Points_WR_HALF b
ON a.player = b.player AND a.team = b.team
GROUP BY a.team
ORDER BY totalteamtargets DESC

--Do Air Yards cause higher fantasy points?
SELECT  a.player, 
		a.team, 
		a.air_yards, 
		b.points,
		point_ranking = RANK() OVER(ORDER BY b.points DESC),
		air_yard_rank = RANK() OVER(ORDER BY a.air_yards DESC)
FROM WRAnalysis..ADV_WR_Stats a LEFT JOIN WRAnalysis..Points_WR_HALF b
ON a.player = b.player AND a.team = b.team
WHERE a.targets > 10
ORDER BY a.air_yards DESC

--Do the players with the highest percentage of team targets score the most?
SELECT  a.player, 
		a.team, 
		a.percent_team_targets,
		b.points,
		team_target_rank = RANK() OVER(ORDER BY a.percent_team_targets DESC),
		point_ranking = RANK() OVER(ORDER BY b.points DESC)
FROM WRAnalysis..ADV_WR_Stats a LEFT JOIN WRAnalysis..Points_WR_HALF b
ON a.player = b.player AND a.team = b.team
WHERE a.targets > 10
ORDER BY a.percent_team_targets DESC

--Players with the most 20+ yard targerts
SELECT  a.player,
		a.team,
		a.[20_plus],
		a.[30_plus],
		b.points,
		[20_plus_rank] = RANK() OVER(ORDER BY a.[20_plus] DESC),
		point_ranking = RANK() OVER(ORDER BY b.points DESC)
FROM WRAnalysis..ADV_WR_Stats a LEFT JOIN WRAnalysis..Points_WR_HALF b
ON a.player = b.player AND a.team = b.team
WHERE a.targets > 10
ORDER BY a.percent_team_targets DESC

--Examine relationship between team yard percentage and total player points
--USE CTE
WITH PercentTeamYards (player, team, games, rec, yds, points, /*team_percentage,*/ team_yards_sum)
AS
(
SELECT  a.player,
		a.team,
		a.games,
		a.rec,
		a.yds,
		b.points,
		--(a.percent_team_targets) * 100 AS team_percentage,
		team_yards_sum = SUM(a.yds) OVER(PARTITION BY a.team)
FROM WRAnalysis..ADV_WR_Stats a LEFT JOIN WRAnalysis..Points_WR_HALF b
ON a.player = b.player AND a.team = b.team
--ORDER BY b.points DESC 
)
SELECT  player,
		team,
		games,
		yds,
		points,
		team_yards_sum,
		ROUND(((yds / team_yards_sum) * 100),2) AS player_yard_percentage,
		point_ranking = RANK() OVER(ORDER BY points DESC),
		team_yard_rank = DENSE_RANK() OVER(ORDER BY team_yards_sum DESC)
FROM PercentTeamYards
WHERE team != 'FA'
ORDER BY player_yard_percentage DESC

 