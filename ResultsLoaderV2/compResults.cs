using FuzzierSharp;
using System;
using System.Collections.Generic;
using System.Data;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using ResultsLoaderV2.Data;

namespace ResultsLoaderV2
{
    class compResults
    {
        private DataTable resultsTable = new DataTable();
        private readonly RankingsRepository repo = new RankingsRepository();

        public compResults()
        {
        }

        public compResults(string compName, DateTime compDate, string sFilePath, string sys, bool major)
        {
            // load csv into datatable
            resultsTable = ConvertCSVtoDataTable(sFilePath);

            int playercount = resultsTable.Rows.Count;
            if (major)
            {
                playercount += 6;
            }

            int maxPoints;
            if (playercount >= 20) maxPoints = 25;
            else if (playercount >= 14) maxPoints = 20;
            else if (playercount >= 10) maxPoints = 15;
            else maxPoints = 10;

            Guid? compID = repo.AddComp(compName, compDate, playercount, maxPoints, sys);

            // for each player check they exist and get ID
            foreach (DataRow placeRow in resultsTable.Rows)
            {
                string playerName = placeRow[1].ToString();
                string armyName = placeRow[3].ToString();
                string AID = placeRow[4].ToString();

                int pnts;
                if (!int.TryParse(placeRow[2].ToString(), out pnts))
                {
                    pnts = 0;
                }

                int plc;
                if (!int.TryParse(placeRow[0].ToString(), out plc))
                {
                    continue;
                }

                string PID = getPID(playerName);

                if (string.IsNullOrEmpty(AID))
                {
                    AID = getAID(armyName);
                }

                if (sys == "REG")
                {
                    AID = "";
                }

                repo.AddPlacingProc(plc, playerName, armyName, pnts.ToString(), "", compID.ToString(), PID, AID);
            }
        }

        public string toString()
        {
            return string.Join(Environment.NewLine,
                resultsTable.Rows.OfType<DataRow>().Select(x => string.Join(" ; ", x.ItemArray)));
        }

        public string getAID(string name)
        {
            if (string.IsNullOrEmpty(name))
                return "";

            var exact = repo.GetArmyIndexByName(name);
            if (exact.Count > 0)
                return exact[0].No.ToString();

            // try partial matches
            List<ArmyIndex> partList = armyMatch(name);
            if (partList.Count > 0)
            {
                Window1 win1 = new Window1(partList, name);
                if (win1.ShowDialog() == true)
                    return win1.playerID.ToString();
            }
            return "";
        }

        public string getPID(string name)
        {
            var exact = repo.GetPlayersByName(name);
            if (exact.Count > 0)
                return exact[0].PlayerID.ToString();

            // try partial matches
            List<Player> partList = nameMatch(name);
            if (partList.Count > 0)
            {
                Window1 win1 = new Window1(partList, name);
                if (win1.ShowDialog() == true)
                    return win1.playerID.ToString();
            }

            // not found, or user said none match: create a new player
            Guid? newpid = repo.AddPlayerProc(name);
            return newpid.ToString();
        }

        public static DataTable ConvertCSVtoDataTable(string sCsvFilePath)
        {
            DataTable dtTable = new DataTable();
            Regex CSVParser = new Regex(",(?=(?:[^\"]*\"[^\"]*\")*(?![^\"]*\"))");

            using (StreamReader sr = new StreamReader(sCsvFilePath))
            {
                string[] headers = sr.ReadLine().Split(',');
                foreach (string header in headers)
                {
                    dtTable.Columns.Add(header);
                }
                while (!sr.EndOfStream)
                {
                    string[] rows = CSVParser.Split(sr.ReadLine());
                    DataRow dr = dtTable.NewRow();
                    for (int i = 0; i < headers.Length; i++)
                    {
                        dr[i] = rows[i].Replace("\"", string.Empty);
                    }
                    dtTable.Rows.Add(dr);
                }
            }
            return dtTable;
        }

        // Top 11 closest player names (same count as before), ranked in memory
        public List<Player> nameMatch(string name)
        {
            return repo.GetPlayers()
                       .OrderByDescending(p => Fuzz.Ratio(name, p.Name ?? ""))
                       .Take(11)
                       .ToList();
        }

        // Top 11 closest army names
        public List<ArmyIndex> armyMatch(string name)
        {
            return repo.GetArmyIndex()
                       .OrderByDescending(a => Fuzz.Ratio(name, a.Army ?? ""))
                       .Take(11)
                       .ToList();
        }

        public void FixIncorrectArmyIDs()
        {
            // ToList() loads everything first, so updating while looping is safe
            foreach (var p in repo.GetPlacingsWithArmyId("0"))
            {
                string correctArmyID = getAID(p.Army);
                if (!string.IsNullOrEmpty(correctArmyID) && correctArmyID != p.ArmyID)
                {
                    repo.SetPlacingArmyId(p.Comp, p.PlayerID, correctArmyID);
                }
            }
        }

        public void nameCombine()
        {
            foreach (Player player in repo.GetPlayers())
            {
                string name = player.Name;
                string dbID;
                bool exists;

                // find similar names
                List<Player> partList = nameMatch(name);

                if (partList.Count > 0)
                {
                    Window1 win1 = new Window1(partList, name);
                    if (win1.ShowDialog() == true)
                    {
                        dbID = win1.playerID.ToString();
                        exists = true;
                    }
                    else { exists = false; }
                }
                // check if they are the same
                // update if so
            }
        }
    }
}