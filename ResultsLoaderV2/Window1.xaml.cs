using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Shapes;

namespace ResultsLoaderV2
{
    /// <summary>
    /// Interaction logic for Window1.xaml
    /// </summary>
    public partial class Window1 : Window
    {
        private bool isarmy;
        public Window1()
        {
            InitializeComponent();
        }
        public Window1(IEnumerable<Player> players, string pname)
        {
            isarmy = false;
            InitializeComponent();
            no.IsEnabled = true;
            yes.IsEnabled = false;
            dg.ItemsSource = players;
            pn.Content = pname;
        }

        public Window1(IEnumerable<ArmyIndex> armies, string aname)
        {
            isarmy = true;
            InitializeComponent();
            no.IsEnabled = true;
            yes.IsEnabled = false;
            dg.ItemsSource = armies;
            pn.Content = aname;
        }

        private string PID;
   
        public string playerID
        {
            get { return PID; }
        }
  

        private void DataGrid_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            yes.IsEnabled = true;
            if (isarmy) 
            {
                ArmyIndex selectedArmy = (ArmyIndex)dg.SelectedItem;
                PID = selectedArmy.No.ToString();
            }
            else
            {
                
                Player selectedPlayer = (Player)dg.SelectedItem;
                PID = selectedPlayer.PlayerID.ToString();
            }



        }

        private void Button_Click(object sender, RoutedEventArgs e)
        {
            Window.GetWindow(this).DialogResult = true;
            Window.GetWindow(this).Close();
        }

        private void no_Click(object sender, RoutedEventArgs e)
        {
            Window.GetWindow(this).DialogResult = false;
            Window.GetWindow(this).Close();
        }
    }
}
