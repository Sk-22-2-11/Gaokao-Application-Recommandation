using Azure.Storage.Blobs;
using System;
using System.Data;
using System.IO;
using System.Text;
using System.Windows;
using System.Windows.Controls;
using ExcelDataReader;
using OfficeOpenXml;

namespace Gaokao_App
{
    public partial class MainWindow : Window
    {
        private DataTable data_wuli;
        private DataTable data_lishi;
        private string blobConnectionString = "blob_connection_string";
        private string containerName = "container_name";

        public MainWindow()
        {
            ExcelPackage.LicenseContext = LicenseContext.NonCommercial;
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            InitializeComponent();
            this.Title = "清北之路志愿推荐系统";

            // Load the Excel files from Azure Blob Storage
            string excelFilePath1 = DownloadBlobFile("2023_pool_Wuli.xlsx");
            string excelFilePath2 = DownloadBlobFile("2023_pool_Lishi.xlsx");

            data_wuli = LoadExcelFile(excelFilePath1);
            data_lishi = LoadExcelFile(excelFilePath2);
        }

        private string DownloadBlobFile(string blobName)
        {
            BlobServiceClient blobServiceClient = new BlobServiceClient(blobConnectionString);
            BlobContainerClient containerClient = blobServiceClient.GetBlobContainerClient(containerName);
            BlobClient blobClient = containerClient.GetBlobClient(blobName);

            string localPath = Path.Combine(Path.GetTempPath(), blobName);
            blobClient.DownloadTo(localPath);

            return localPath;
        }

        private DataTable LoadExcelFile(string filePath)
        {
            using (var stream = File.Open(filePath, FileMode.Open, FileAccess.Read))
            {
                using (var reader = ExcelReaderFactory.CreateReader(stream, new ExcelReaderConfiguration()
                {
                    FallbackEncoding = Encoding.GetEncoding("GB2312")
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

        private static readonly HttpClient client = new HttpClient();

        private async Task<string> CallAzureMLApiAsync(string apiUrl, string apiKey, string requestBody)
        {
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", apiKey);

            var content = new StringContent(requestBody, Encoding.UTF8, "application/json");
            var response = await client.PostAsync(apiUrl, content);

            return await response.Content.ReadAsStringAsync();
        }

        // Example usage of the Azure ML API call
        private async void BtnAnalyze_Click(object sender, RoutedEventArgs e)
        {
            string apiUrl = "your_azure_ml_api_url";
            string apiKey = "your_api_key";
            string requestBody = "{ \"data\": [ /* your input data */ ] }";

            string result = await CallAzureMLApiAsync(apiUrl, apiKey, requestBody);
            MessageBox.Show(result);
        }

        private void GenerateHtmlReport(DataTable dataTable, string fileName)
        {
            string html = "<html><head><title>Report</title></head><body>";
            html += "<table border='1'><tr>";

            // Add header row
            foreach (DataColumn column in dataTable.Columns)
            {
                html += "<th>" + column.ColumnName + "</th>";
            }
            html += "</tr>";

            // Add data rows
            foreach (DataRow row in dataTable.Rows)
            {
                html += "<tr>";
                foreach (var item in row.ItemArray)
                {
                    html += "<td>" + item.ToString() + "</td>";
                }
                html += "</tr>";
            }

            html += "</table></body></html>";

            File.WriteAllText(fileName, html);
        }

        private void BtnConfirm_Click(object sender, RoutedEventArgs e)
        {
            string desktopPath = Environment.GetFolderPath(Environment.SpecialFolder.Desktop);
            string outputFilePath = Path.Combine(desktopPath, "report.html");

            GenerateHtmlReport(data_wuli, outputFilePath);
            MessageBox.Show("Report generated: " + outputFilePath);

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
