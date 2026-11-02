using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ResultsLoaderV2

{
    // Table: player
    public class Player
    {
        public Guid? PlayerID { get; set; }
        public string Name { get; set; }
    }

    // Table: placing
    public class Placing
    {
        public int? Position { get; set; }
        public string Name { get; set; }
        public string Army { get; set; }
        public string Score { get; set; }
        public string Points { get; set; }
        public string Comp { get; set; }
        public string PlayerID { get; set; }   // string here, Guid in player
        public string ArmyID { get; set; }     // string here, int in army
    }

    // Table: army  (the "Army" column is mapped to Name, because C# won't
    // allow a property with the same name as its class)
    public class Army
    {
        public int ArmyID { get; set; }
        public string Name { get; set; }
        public string Dates { get; set; }
        public string ListSet { get; set; }
    }

    // Table: comp  (the "Comp" column is mapped to Name for the same reason)
    public class Comp
    {
        public Guid CompID { get; set; }
        public string Name { get; set; }
        public DateTime? Date { get; set; }
        public int? Players { get; set; }
        public int? MaxPoints { get; set; }
        public bool? Old { get; set; }
        public string Region { get; set; }
    }

    // Table/view: ArmyIndex
    public class ArmyIndex
    {
        public int No { get; set; }
        public string Army { get; set; }
        public string Dates { get; set; }
        public string Terrain_1 { get; set; }
        public string Terrain_2 { get; set; }
        public string Terrain_3 { get; set; }
        public string Region { get; set; }
    }
}