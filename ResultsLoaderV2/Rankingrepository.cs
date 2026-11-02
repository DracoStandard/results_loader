using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using Dapper;

namespace ResultsLoaderV2.Data
{
    public class RankingsRepository
    {
        // ---------- player ----------
        public List<Player> GetPlayers()
        {
            using (var c = Db.Open())
                return c.Query<Player>(
                    "SELECT PlayerID, Name FROM dbo.[players] ORDER BY Name").ToList();
        }

        public Player GetPlayer(Guid id)
        {
            using (var c = Db.Open())
                return c.QuerySingleOrDefault<Player>(
                    "SELECT PlayerID, Name FROM dbo.[players] WHERE PlayerID = @id", new { id });
        }

        public void AddPlayer(Player p)
        {
            if (p.PlayerID == null) p.PlayerID = Guid.NewGuid();
            using (var c = Db.Open())
                c.Execute("INSERT INTO dbo.[players] (PlayerID, Name) VALUES (@PlayerID, @Name)", p);
        }

        public void UpdatePlayer(Player p)
        {
            using (var c = Db.Open())
                c.Execute("UPDATE dbo.[players] SET Name = @Name WHERE PlayerID = @PlayerID", p);
        }

        // ---------- army ----------
        public List<Army> GetArmies()
        {
            using (var c = Db.Open())
                return c.Query<Army>(
                    "SELECT ArmyID, [Army] AS Name, Dates, ListSet FROM dbo.[armies] ORDER BY [Army]").ToList();
        }

        public void AddArmy(Army a)
        {
            using (var c = Db.Open())
                c.Execute("INSERT INTO dbo.[armies] (ArmyID, [Army], Dates, ListSet) VALUES (@ArmyID, @Name, @Dates, @ListSet)", a);
        }

        public void UpdateArmy(Army a)
        {
            using (var c = Db.Open())
                c.Execute("UPDATE dbo.[armies] SET [Army] = @Name, Dates = @Dates, ListSet = @ListSet WHERE ArmyID = @ArmyID", a);
        }

        // ---------- comp ----------
        private const string CompSelect =
            "SELECT CompID, [Comp] AS Name, [Date], Players, MaxPoints, Old, Region FROM dbo.[comps]";

        public List<Comp> GetComps()
        {
            using (var c = Db.Open())
                return c.Query<Comp>(CompSelect + " ORDER BY [Date] DESC").ToList();
        }

        public void AddComp(Comp comp)
        {
            if (comp.CompID == Guid.Empty) comp.CompID = Guid.NewGuid();
            using (var c = Db.Open())
                c.Execute(@"INSERT INTO dbo.[comps] (CompID, [Comp], [Date], Players, MaxPoints, Old, Region)
                            VALUES (@CompID, @Name, @Date, @Players, @MaxPoints, @Old, @Region)", comp);
        }

        public void UpdateComp(Comp comp)
        {
            using (var c = Db.Open())
                c.Execute(@"UPDATE dbo.[comps] SET [Comp] = @Name, [Date] = @Date, Players = @Players,
                            MaxPoints = @MaxPoints, Old = @Old, Region = @Region
                            WHERE CompID = @CompID", comp);
        }

        // ---------- placing ----------
        private const string PlacingSelect =
            "SELECT [position], [name], [army], [score], [points], [comp], PlayerID, ArmyID FROM dbo.[placings]";

        public List<Placing> GetPlacingsForComp(string comp)
        {
            using (var c = Db.Open())
                return c.Query<Placing>(PlacingSelect + " WHERE [comp] = @comp ORDER BY [position]", new { comp }).ToList();
        }

        public List<Placing> GetPlacingsForPlayer(string playerId)
        {
            using (var c = Db.Open())
                return c.Query<Placing>(PlacingSelect + " WHERE PlayerID = @playerId", new { playerId }).ToList();
        }

        public void AddPlacing(Placing p)
        {
            using (var c = Db.Open())
                c.Execute(@"INSERT INTO dbo.[placings] ([position], [name], [army], [score], [points], [comp], PlayerID, ArmyID)
                            VALUES (@Position, @Name, @Army, @Score, @Points, @Comp, @PlayerID, @ArmyID)", p);
        }

        // Primary key is comp + PlayerID
        public void UpdatePlacing(Placing p)
        {
            using (var c = Db.Open())
                c.Execute(@"UPDATE dbo.[placings] SET [position] = @Position, [name] = @Name, [army] = @Army,
                            [score] = @Score, [points] = @Points, ArmyID = @ArmyID
                            WHERE [comp] = @Comp AND PlayerID = @PlayerID", p);
        }

        public void DeletePlacing(string comp, string playerId)
        {
            using (var c = Db.Open())
                c.Execute("DELETE FROM dbo.[placings] WHERE [comp] = @comp AND PlayerID = @playerId", new { comp, playerId });
        }

        public List<Placing> GetPlacingsWithArmyId(string armyId)
        {
            using (var c = Db.Open())
                return c.Query<Placing>(PlacingSelect + " WHERE ArmyID = @armyId", new { armyId }).ToList();
        }

        public void SetPlacingArmyId(string comp, string playerId, string armyId)
        {
            using (var c = Db.Open())
                c.Execute("UPDATE dbo.[placings] SET ArmyID = @armyId WHERE [comp] = @comp AND PlayerID = @playerId",
                          new { comp, playerId, armyId });
        }

        public List<Player> GetPlayersByName(string name)
        {
            using (var c = Db.Open())
                return c.Query<Player>("SELECT PlayerID, Name FROM dbo.[players] WHERE Name = @name", new { name }).ToList();
        }

        // ---------- ArmyIndex ----------
        private const string ArmyIndexSelect =
            "SELECT [No], [Army], Dates, Terrain_1, Terrain_2, Terrain_3, Region FROM dracostandard.[ArmyIndex]";

        public List<ArmyIndex> GetArmyIndex()
        {
            using (var c = Db.Open())
                return c.Query<ArmyIndex>(ArmyIndexSelect + " ORDER BY [No]").ToList();
        }

        public List<ArmyIndex> GetArmyIndexByName(string army)
        {
            using (var c = Db.Open())
                return c.Query<ArmyIndex>(ArmyIndexSelect + " WHERE [Army] = @army", new { army }).ToList();
        }

        // ---------- stored procedures ----------
        // Parameter names taken from DataClasses1.designer.cs

        public Guid? AddComp(string name, DateTime date, int players, int maxPoints, string sys)
        {
            var p = new DynamicParameters();
            p.Add("@CompName", name);
            p.Add("@CompDate", date, DbType.Date);
            p.Add("@noOfPlayers", players);
            p.Add("@MaxPoints", maxPoints);
            p.Add("@sys", sys);
            p.Add("@returnCompID", dbType: DbType.Guid, direction: ParameterDirection.InputOutput, value: Guid.Empty);
            using (var c = Db.Open())
                c.Execute("dracostandard.addComp", p, commandType: CommandType.StoredProcedure);
            return p.Get<Guid?>("@returnCompID");
        }

        // Schema not specified in the original code, so this uses your login's default schema.
        // If you get "Could not find stored procedure", change it to "dracostandard.updateOldComps".
        public void UpdateOldComps()
        {
            using (var c = Db.Open())
                c.Execute("updateOldComps", commandType: CommandType.StoredProcedure);
        }

        public Guid? AddPlayerProc(string name)
        {
            var p = new DynamicParameters();
            p.Add("@playerName", name);
            p.Add("@returnID", dbType: DbType.Guid, direction: ParameterDirection.InputOutput, value: Guid.Empty);
            using (var c = Db.Open())
                c.Execute("dracostandard.addPlayer", p, commandType: CommandType.StoredProcedure);
            return p.Get<Guid?>("@returnID");
        }

        public void AddPlacingProc(int position, string name, string army, string score,
                                   string points, string comp, string playerId, string armyId)
        {
            var p = new DynamicParameters();
            p.Add("@position", position);
            p.Add("@name", name);
            p.Add("@army", army);
            p.Add("@score", score);
            p.Add("@points", points);
            p.Add("@comp", comp);
            p.Add("@PlayerID", playerId);
            p.Add("@ArmyID", armyId);
            using (var c = Db.Open())
                c.Execute("dracostandard.addPlacing", p, commandType: CommandType.StoredProcedure);
        }
    }
}