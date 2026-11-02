using Microsoft.Win32;
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
using System.Windows.Navigation;
using System.Windows.Shapes;

namespace ResultsLoaderV2
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
        }

        private void Button_Click(object sender, RoutedEventArgs e)
        {
            DateTime dt = DateTime.Now;

            string sFilePath = "";
            //get path
            OpenFileDialog openFileDialog = new OpenFileDialog();
            openFileDialog.InitialDirectory = @"C:\Users\draco_otbrc86\OneDrive\MEG Rankings\resultsForUpload\";
            openFileDialog.Filter = "csv files (*.csv) |*.csv";
            if (openFileDialog.ShowDialog() == true)
            {
                sFilePath = openFileDialog.FileName;
            }

            bool isMajor = MajorToggleButton.IsChecked == true;

            compResults cr = new compResults(CompNameTxt.Text, dt, sFilePath, SystemTxt.Text, isMajor);

            //idOutput.Content = cr.getID("paul not real 2");
        }

        private void Button_Click_1(object sender, RoutedEventArgs e)
        {
            string name = "Hammy";
            nameSort ns = new nameSort(name);

        }

        private void FixIncorrectArmyIDs_Click(object sender, RoutedEventArgs e)
        {
            compResults compResultsInstance = new compResults();
            compResultsInstance.FixIncorrectArmyIDs();
            MessageBox.Show("Incorrect Army IDs have been fixed.", "Operation Complete", MessageBoxButton.OK, MessageBoxImage.Information);
        }
        private void UpdateOldComps_Click(object sender, RoutedEventArgs e)
        {
            var repo = new Data.RankingsRepository();
            repo.UpdateOldComps();
            MessageBox.Show("Old competitions updated.", "Update Complete", MessageBoxButton.OK, MessageBoxImage.Information);
        }
    }


    }

