using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Data;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Timers;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using ExcelDataReader;
using OfficeOpenXml;


namespace Gaokao_App
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        private Timer timer;
        private DataTable data_wuli;
        private DataTable data_lishi;

        public MainWindow()
        {
            ExcelPackage.LicenseContext = LicenseContext.NonCommercial;
            // 注册 CodePagesEncodingProvider
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);

            InitializeComponent();
            this.Title = "清北之路志愿推荐系统";
            // 加载第一个Excel文件
            string excelFilePath1 = "2023_pool_Wuli.xlsx";
            data_wuli = LoadExcelFile(excelFilePath1);

            // 加载第二个Excel文件
            string excelFilePath2 = "2023_pool_Lishi.xlsx";
            data_lishi = LoadExcelFile(excelFilePath2);

            // 调用LoadExcelFile方法来加载Excel文件
            DataTable LoadExcelFile(string filePath)
            {
                using (var stream = File.Open(filePath, FileMode.Open, FileAccess.Read))
                {
                    using (var reader = ExcelReaderFactory.CreateReader(stream, new ExcelReaderConfiguration()
                    {
                        FallbackEncoding = Encoding.GetEncoding("GB2312") // 使用指定编码（例如 1252）进行读取
                    }))
                    {
                        var result = reader.AsDataSet(new ExcelDataSetConfiguration
                        {
                            ConfigureDataTable = (_) => new ExcelDataTableConfiguration
                            {
                                UseHeaderRow = true
                            }
                        });

                        return result.Tables[0];
                    }
                }
            }
        }

        private void BtnConfirm_Click(object sender, RoutedEventArgs e)
        {
            string name = txtName.Text;
            string subject = cmbSubject.Text;
            int rank = int.Parse(txtRank.Text);
            int rankMax = int.Parse(txtRankMax.Text);
            int rankMin = int.Parse(txtRankMin.Text);

            DataTable filteredData;
            if (subject == "理科")
            {
                filteredData = FilterData(data_wuli, rankMin, rankMax);
            }
            else
            {
                filteredData = FilterData(data_lishi, rankMin, rankMax);
            }

            // 生成新的 Excel 表格
            // 生成文件的目录
            string desktopPath = Environment.GetFolderPath(Environment.SpecialFolder.Desktop);
            string outputFilePath = Path.Combine(desktopPath, "志愿2023-" + subject + "-" + name + "-" + rank + ".xlsx");

            string excelFileName = $"志愿2023-{subject}-{name}-{rank}.xlsx";
            GenerateExcel(filteredData, outputFilePath);

            StartProgressBar();
        }

        private DataTable FilterData(DataTable dataTable, int rankMin, int rankMax)
        {
            DataView dataView = dataTable.DefaultView;
            dataView.RowFilter = $"[去年提档位次] <= {rankMin} AND [去年提档位次] >= {rankMax}";
            DataTable filteredData = dataView.ToTable();
            return filteredData;
        }

        private void GenerateExcel(DataTable dataTable, string fileName)
        {
            using (var excelPackage = new ExcelPackage())
            {
                ExcelWorksheet worksheet = excelPackage.Workbook.Worksheets.Add("Sheet1");
                worksheet.Cells.LoadFromDataTable(dataTable, true);

                FileInfo fileInfo = new FileInfo(fileName);
                excelPackage.SaveAs(fileInfo);
            }
        }

        private void StartProgressBar()
        {
            progressBar.Value = progressBar.Minimum;
            progressBar.Value = 0;

            timer = new Timer();
            timer.Interval = 1000; // 1秒钟
            timer.Elapsed += TimerElapsed;
            timer.Start();
        }

        private void TimerElapsed(object sender, ElapsedEventArgs e)
        {
            Dispatcher.Invoke(() =>
            {
                progressBar.Value += 1;

                if (progressBar.Value >= progressBar.Maximum)
                {
                    timer.Stop();
                }
            });
        }

    }
}
