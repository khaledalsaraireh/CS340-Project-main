from flask import Flask, render_template, redirect       #type: ignore
from flask_mysqldb import MySQL                          #type: ignore
from flask import request                                #type: ignore

# Citation for the following
# Date: 11/17/24
# Adapted from Flask Starter App Guide
# Source URL: https://github.com/osu-cs340-ecampus/flask-starter-app/blob/master/bsg_people_app/app.py


app = Flask(__name__)

'''app.config['MYSQL_HOST'] = 'classmysql.engr.oregonstate.edu'
app.config['MYSQL_USER'] = 'cs340_palmerj2'
app.config['MYSQL_PASSWORD'] = '0690' # last 4 of onid
app.config['MYSQL_DB'] = 'cs340_palmerj2'
app.config['MYSQL_CURSORCLASS'] = "DictCursor" '''


app.config['MYSQL_HOST'] ='localhost'
app.config['MYSQL_USER'] ='root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = '340testenv'
app.config['MYSQL_CURSORCLASS'] = "DictCursor" 
mysql = MySQL(app) 


''' # localhost db info, commented out '''

# ---------- Home Page Routes Start ----------
@app.route("/")
def home():
    return render_template("index.j2")
# ---------- Home Page Routes End ----------




# ---------- Players Routes Start ----------
@app.route("/players", methods=["POST", "GET"])
def players():
    cur = mysql.connection.cursor()
    if request.method == "GET":
        query = "SELECT playerID, name, originTeamNFL, playerFantasyPoints, position FROM Players"
        cur.execute(query)
        player_data = cur.fetchall()

    return render_template("players.j2", player_data = player_data)

@app.route("/add_player", methods=["POST", "GET"])
def add_player():
    cur = mysql.connection.cursor()
    if request.method == "GET":
        return render_template("add_player.j2")
    if request.method == "POST":
        player_name = request.form["playerName"]
        nfl_team = request.form["nfl-team"]
        fantasy_points = request.form["fantasyPoints"]
        position = request.form["position"]
        query = "INSERT INTO Players (name, originTeamNFL, playerFantasyPoints, position) VALUES (%s, %s, %s, %s);"
        cur.execute(query, (player_name, nfl_team, fantasy_points, position))
        mysql.connection.commit()
        return redirect("/players")

@app.route("/delete_player/<int:id>")
def delete_player(id):
    query = "DELETE from Players WHERE playerID = '%s';"
    cur = mysql.connection.cursor()
    cur.execute(query, (id,))
    mysql.connection.commit()
    return redirect("/players")


@app.route("/update_player/<int:playerId>", methods =["POST", "GET"])
def update_player(playerId):
    cur = mysql.connection.cursor()
    if request.method == "POST":
        playerName = request.form["playerName"]
        nflTeam = request.form["nfl-team"]
        fantasyPoints = request.form["fantasyPoints"]
        position = request.form["position"]
        query = "UPDATE Players SET Players.name = %s, Players.originTeamNFL = %s, Players.playerFantasyPoints = %s, Players.position = %s WHERE Players.playerID = %s"
        cur.execute(query, (playerName, nflTeam, fantasyPoints, position, playerId ))
        mysql.connection.commit()
    if request.method == "GET":
        query = "SELECT playerID, name, originTeamNFL, playerFantasyPoints, position FROM Players WHERE playerID = %s"
        cur.execute(query, (playerId,))
        player_data = cur.fetchall()
        return render_template("update_player.j2", player_data=player_data)
    return redirect("/players")

# ---------- Players Routes End ----------



# ---------- Team Routes Start ----------
@app.route("/teams", methods = ["GET", "POST"])
def teams():
    cur = mysql.connection.cursor()
    if request.method == "GET":
        query = "SELECT userName FROM TeamOwners"
        cur.execute(query)
        team_owner_names = cur.fetchall()
        query = "SELECT teamID, teamName, wins, losses, teamFantasyPoints, TeamOwners.userName, Leagues.leagueName FROM Teams LEFT JOIN TeamOwners ON Teams.teamOwnerID = TeamOwners.teamOwnerID LEFT JOIN Leagues ON Teams.leagueID = Leagues.leagueID;"
        cur.execute(query)
        teams_data = cur.fetchall()
    
    return render_template("teams.j2", team_owner_names=team_owner_names, teams_data = teams_data)

@app.route("/delete_team/<int:id>")
def delete_team(id):
    query = "DELETE Teams FROM Teams WHERE teamID = '%s'"
    cur = mysql.connection.cursor()
    cur.execute(query, (id,))
    mysql.connection.commit()
    return redirect("/teams")

@app.route("/add_team", methods=["GET","POST"])
def add_team():
    cur = mysql.connection.cursor()
    if request.method == "GET":
        query = "SELECT userName FROM TeamOwners"
        cur.execute(query)
        team_owner_names = cur.fetchall()
        query = "SELECT leagueName FROM Leagues"
        cur.execute(query)
        league_names = cur.fetchall()
        return render_template("add_team.j2", team_owner_names=team_owner_names, league_names = league_names)
    if request.method == "POST":
        teamName = request.form["name"]
        wins = request.form["wins"]
        losses = request.form["losses"]
        fantasyPoints = request.form["teamFantasyPoints"]
        owner = request.form["teamOwnerName"]
        league = request.form["leagueName"]
        query = """
        INSERT INTO Teams (teamName, wins, losses, teamFantasyPoints, teamOwnerID, leagueID)
        VALUES (
            %s, 
            %s, 
            %s, 
            %s, 
            (SELECT teamOwnerID FROM TeamOwners WHERE userName = %s), 
            (SELECT leagueID FROM Leagues WHERE leagueName = %s)
        );
        """
        cur.execute(query, (teamName, wins, losses, fantasyPoints, owner, league))
        mysql.connection.commit()
        return redirect("/teams")

@app.route("/update_team/<int:teamId>", methods =["POST", "GET"])
def update_team(teamId):
    cur = mysql.connection.cursor()
    if request.method == "POST":
        teamName = request.form["name"]
        wins = request.form["wins"]
        losses = request.form["losses"]
        fantasyPoints = request.form["teamFantasyPoints"]
        owner = request.form["teamOwnerName"]
        league = request.form["leagueName"]
        query = """
        UPDATE Teams
        SET 
            teamName = %s, 
            wins = %s, 
            losses = %s, 
            teamFantasyPoints = %s, 
            teamOwnerID = (SELECT teamOwnerID FROM TeamOwners WHERE userName = %s), 
            leagueID = (SELECT leagueID FROM Leagues WHERE leagueName = %s)
        WHERE teamID = %s
        """
        cur.execute(query, (teamName, wins, losses, fantasyPoints, owner, league, teamId))
        mysql.connection.commit()
        return redirect("/teams")
    if request.method == "GET":
        query = "SELECT userName FROM TeamOwners"
        cur.execute(query)
        team_owner_names = cur.fetchall()
        query = """SELECT teamID, teamName, wins, losses, teamFantasyPoints, TeamOwners.userName, Leagues.leagueName 
        FROM Teams LEFT JOIN TeamOwners ON Teams.teamOwnerID = TeamOwners.teamOwnerID 
        LEFT JOIN Leagues ON Teams.leagueID = Leagues.leagueID
        WHERE teamID = %s"""
        cur.execute(query, (teamId,))
        team_data = cur.fetchall()
        query = "SELECT leagueName FROM Leagues"
        cur.execute(query)
        league_names = cur.fetchall()
        return render_template("update_team.j2", team_owner_names = team_owner_names, team_data = team_data, league_names = league_names)
   
# ---------- Team Routes End ----------



# ---------- Team Owner Routes Start ----------
@app.route("/team_owners", methods = ["GET", "POST"])
def team_owners():
    cur = mysql.connection.cursor()
    if request.method == "GET":
        query = """
        SELECT teamOwnerID, userName, email, dateOfBirth
        FROM TeamOwners;
        """
        cur.execute(query)
        data = cur.fetchall()
    if request.method == "POST":
        name = request.form["userName"]
        email = request.form["email"]
        dob = request.form["dateOfBirth"]
        query = """
        INSERT INTO TeamOwners (userName, email, dateOfBirth)
        VALUES (%s, %s, %s);
        """
        cur.execute(query, (name, email, dob))
        mysql.connection.commit()
        return redirect("/team_owners")

    return render_template("team_owners.j2", team_owners_data = data)


@app.route("/delete_owner/<int:id>")
def delete_team_owner(id):
    query = "DELETE TeamOwners FROM TeamOwners WHERE teamOwnerID = %s"
    cur = mysql.connection.cursor() 
    cur.execute(query, (id, ))
    mysql.connection.commit()
    return redirect("/team_owners")


@app.route("/update_team_owner", methods = ["POST"])
def update_team_owner():
    name = request.form["userName"]
    email = request.form["email"]
    dob = request.form["dateOfBirth"]
    ownerID = request.form["teamOwnerID"]
    query = """
    UPDATE TeamOwners
    SET userName = %s, email = %s, dateOfBirth = %s
    WHERE teamOwnerID = %s;
    """
    cur = mysql.connection.cursor() 
    cur.execute(query, (name, email, dob, ownerID))
    mysql.connection.commit()
    return redirect("/team_owners")
# ---------- Team Owner Routes End ----------

# --------- League Routes Start -----------
@app.route("/leagues", methods = ["GET", "POST"])
def leagues():

    if request.method == "POST":
        
        leagueName = request.form["leaguename"]
        isActive = request.form["active"]
        query = """
        INSERT INTO Leagues (leagueName, isActive)
        VALUES (%s, %s);
        """
        cur = mysql.connection.cursor()
        cur.execute(query, (leagueName, isActive))
        mysql.connection.commit()
        return redirect("/leagues")
    



    if request.method == "GET":
        query = "SELECT leagueID, leagueName, isActive FROM Leagues"
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()

    return render_template("leagues.j2", data=data)

@app.route("/edit_league/<int:leagueID>", methods=["POST", "GET"])
def edit_league(leagueID):
    if request.method == "GET":
        query = "SELECT * FROM Leagues WHERE leagueID = %s" % (leagueID)
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()
        return render_template("edit_leagues.j2", data=data)
    if request.method == "POST":
        if request.form.get("Submit_Edits"):
            leagueID = request.form["leagueID"]
            leagueName = request.form["leaguename"]
            isActive = request.form["active"]
            query = "UPDATE Leagues SET leagueName = %s, isActive = %s WHERE leagueID = %s"
            cur = mysql.connection.cursor()
            cur.execute(query,(leagueName, isActive, leagueID))
            mysql.connection.commit()



        return redirect("/leagues")
@app.route("/delete_league/<int:leagueID>")
def delete_league(leagueID):
    query = "DELETE FROM Leagues WHERE leagueID = %s"
    cur = mysql.connection.cursor()
    cur.execute(query, (leagueID,))
    mysql.connection.commit() 
    return redirect("/leagues")      
# ---------------- End League routes  -----------------------


# --------------- Matches routes start------------------------
@app.route("/matches", methods=["POST","GET"])
def matches():
    if request.method =="GET":
        query = """SELECT m.matchID, m.weekPlayed, m.homeTeamScore, m.awayTeamScore, h.teamName, a.teamName 
        FROM Matches as m
        JOIN Teams as h 
        ON h.teamID = m.homeTeamID
        JOIN Teams as a
        ON a.teamID = m.awayTeamID"""
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()

        query2 = "SELECT teamID, teamName FROM Teams"
        cur = mysql.connection.cursor()
        cur.execute(query2)
        teamData = cur.fetchall()

    if request.method =="POST":
        weekPlayed = request.form["week"]
        homeTeamScore = request.form["hometeamscore"]
        awayTeamScore = request.form["awayteamscore"]
        homeTeamId = request.form["home"]
        awayTeamId = request.form["away"]
        query = """INSERT INTO Matches(weekPlayed, homeTeamScore, awayTeamScore, homeTeamID, awayTeamID)
                VALUES(%s,%s,%s,%s,%s)"""
        cur = mysql.connection.cursor()
        cur.execute(query,(weekPlayed,homeTeamScore,awayTeamScore,homeTeamId,awayTeamId))
        mysql.connection.commit()
        return redirect("/matches")
    
    return render_template("matches.j2", data=data, teamData=teamData)
@app.route("/delete_match/<int:matchID>")
def delete_match(matchID):
    query = "DELETE FROM Matches WHERE matchID = %s"
    cur = mysql.connection.cursor()
    cur.execute(query,(matchID,))
    mysql.connection.commit()
    return redirect("/matches")
@app.route("/edit_match/<int:matchID>", methods=["POST", "GET"])
def edit_match(matchID):
    if request.method =="GET":
        query = "SELECT * FROM Matches WHERE MatchID = %s" % (matchID)
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()
        
        query2 = "SELECT teamID, teamName FROM Teams"
        cur = mysql.connection.cursor()
        cur.execute(query2)
        teamData = cur.fetchall()
        return render_template("edit_matches.j2", data=data, teamData=teamData)
    if request.method =="POST":
        weekPlayed = request.form["week"]
        homeTeamScore = request.form["hometeamscore"]
        awayTeamScore = request.form["awayteamscore"]
        homeTeamId = request.form["home"]
        awayTeamId = request.form["away"]
        matchId = request.form["matchid"]
        query = """UPDATE Matches SET weekPlayed =%s, homeTeamScore = %s, awayTeamScore = %s, homeTeamID = %s, awayTeamID = %s WHERE matchID = %s"
                VALUES(%s,%s,%s,%s,%s,%s)"""
        cur = mysql.connection.cursor()
        cur.execute(query,(weekPlayed,homeTeamScore,awayTeamScore,homeTeamId,awayTeamId,matchId))
        mysql.connection.commit()
    return redirect("/matches")
    
    

# --------------- Matches routes End------------------------
  
# ---------- Players In Teams Routes Start ----------
@app.route("/team_rosters", methods = ["POST", "GET"])
def playerInTeam():
    cur = mysql.connection.cursor()
    if request.method == "GET":
        query = """
        SELECT playerTeamStatusID, Teams.teamName, Players.name, playerActiveOnTeam
        FROM PlayerHasTeam
        JOIN Teams ON PlayerHasTeam.teamID = Teams.teamID
        JOIN Players ON PlayerHasTeam.playerID = Players.playerID
        ORDER BY playerTeamStatusID;
        """
        cur.execute(query)
        data = cur.fetchall()
        query = "SELECT name FROM Players"
        cur.execute(query)
        player_name_data = cur.fetchall()
        query = "SELECT teamName from Teams"
        cur.execute(query)
        team_name_data = cur.fetchall()
    if request.method == "POST":
        playerName = request.form["playerName"]
        teamName = request.form["teamName"]
        status = request.form["isActive"]
        query = """
        INSERT INTO PlayerHasTeam(playerID, teamID, playerActiveOnTeam)
        VALUES (
            (SELECT playerID FROM Players WHERE name = %s), 
            (SELECT teamID FROM Teams WHERE teamName = %s),
            %s
        )
        """
        cur.execute(query, (playerName, teamName, status))
        mysql.connection.commit()
        return redirect("/team_rosters")
    return render_template("team_rosters.j2", 
                           data = data, 
                           player_name_data = player_name_data,
                           team_name_data = team_name_data)


@app.route("/delete_playerInTeam/<int:id>")
def delete_playerInTeam(id):
    query = "DELETE PlayerHasTeam FROM PlayerHasTeam WHERE playerTeamStatusID = %s"
    cur = mysql.connection.cursor()
    cur.execute(query, (id,))
    mysql.connection.commit() 
    return redirect("/team_rosters")     


@app.route("/update_playerInTeam", methods = ["POST"])
def update_playerInTeam():
    id = request.form["playerInTeamID"]
    name = request.form["playerName"]
    teamName = request.form["teamName"]
    active = request.form["isActive"]
    query = """
    UPDATE PlayerHasTeam
    SET 
        playerID = (SELECT playerID FROM Players WHERE name = %s), 
        teamID = (SELECT teamID FROM Teams WHERE teamName = %s), 
        playerActiveOnTeam = %s
    WHERE playerTeamStatusID = %s
    """
    cur = mysql.connection.cursor() 
    cur.execute(query, (name, teamName, active, id))
    mysql.connection.commit()
    return redirect("/team_rosters")
# ---------- Players In Teams Routes End ----------
       
if __name__ == "__main__":
    app.run(port=1122, debug=True)