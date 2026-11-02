using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using FuzzierSharp;
using ResultsLoaderV2.Data;

namespace ResultsLoaderV2
{
    internal class nameSort
    {
        private readonly string name;
        private DataTable resultsTable = new DataTable();
        private readonly RankingsRepository repo = new RankingsRepository();

        public nameSort(string name)
        {
            this.name = name;

            // top 11 closest player names
            List<Player> fuzPlayerList = repo.GetPlayers()
                .OrderByDescending(p => Fuzz.Ratio(name, p.Name ?? ""))
                .Take(11)
                .ToList();

            Window1 win1 = new Window1(fuzPlayerList, name);
            bool? dialogResult = win1.ShowDialog();
        }

        public string getPID(string name)
        {
            var match = repo.GetPlayersByName(name).FirstOrDefault();
            return match == null ? "" : match.PlayerID.ToString();
        }
    }
}