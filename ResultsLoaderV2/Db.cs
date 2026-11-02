using System.Configuration;
using Microsoft.Data.SqlClient;

namespace ResultsLoaderV2
{


    public static class Db
    {
        private static readonly string ConnStr =
            ConfigurationManager.ConnectionStrings["Draco"].ConnectionString;

        public static SqlConnection Open()
        {
            var conn = new SqlConnection(ConnStr);
            conn.Open();
            return conn;
        }
    }
}
