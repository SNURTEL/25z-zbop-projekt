import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Box
} from '@mui/material';
import Grid from '@mui/material/Grid';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Bar, Line, Chart } from 'react-chartjs-2';
import { messages } from '../form/messages';
import './styles.scss';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export type PredictionData = {
  day: string;
  orderAmount: number;
  consumedAmount: number;
  remainingAmount: number;
  unit: string;
};

export type PredictionResultProps = {
  data: PredictionData[];
  demandData?: number[];
  purchaseCosts?: number[];
  transportCost?: number;
};

const PredictionResult: React.FC<PredictionResultProps> = ({ data, demandData, purchaseCosts, transportCost }) => {
  // Prepare chart data
  const dayLabels = data.map((row) => row.day);
  const orderAmounts = data.map((row) => row.orderAmount);
  const consumedAmounts = data.map((row) => row.consumedAmount);
  const inventoryAmounts = data.map((row) => row.remainingAmount);
  
  // Calculate costs for charts
  const dailyPurchaseCosts = purchaseCosts 
    ? orderAmounts.map((order, i) => order * purchaseCosts[i])
    : [];
  const dailyTransportCosts = transportCost
    ? orderAmounts.map((order) => order > 0 ? transportCost : 0)
    : [];
  const dailyTotalCosts = dailyPurchaseCosts.length > 0
    ? dailyPurchaseCosts.map((cost, i) => cost + (dailyTransportCosts[i] || 0))
    : [];
  const cumulativeCosts = dailyTotalCosts.reduce((acc: number[], cost) => {
    const prev = acc.length > 0 ? acc[acc.length - 1] : 0;
    acc.push(prev + cost);
    return acc;
  }, []);

  // Chart 1: Demand vs Inventory
  const demandInventoryData = {
    labels: dayLabels,
    datasets: [
      {
        type: 'bar' as const,
        label: 'Demand (kg)',
        data: demandData || consumedAmounts,
        backgroundColor: 'rgba(173, 216, 230, 0.7)',
        yAxisID: 'y',
      },
      {
        type: 'line' as const,
        label: 'Inventory (kg)',
        data: inventoryAmounts,
        borderColor: 'rgb(0, 0, 139)',
        backgroundColor: 'rgba(0, 0, 139, 0.1)',
        borderWidth: 2,
        tension: 0.1,
        yAxisID: 'y1',
      },
    ],
  };

  // Chart 2: Order Amounts
  const orderData = {
    labels: dayLabels,
    datasets: [
      {
        label: 'Order Amount (kg)',
        data: orderAmounts,
        backgroundColor: 'rgba(34, 139, 34, 0.7)',
      },
    ],
  };

  // Chart 3: Daily Costs
  const costsData = {
    labels: dayLabels,
    datasets: [
      {
        label: 'Purchase Cost (PLN)',
        data: dailyPurchaseCosts,
        backgroundColor: 'rgba(255, 165, 0, 0.7)',
      },
      {
        label: 'Transport Cost (PLN)',
        data: dailyTransportCosts,
        backgroundColor: 'rgba(220, 20, 60, 0.7)',
      },
    ],
  };

  // Chart 4: Cumulative Cost
  const cumulativeData = {
    labels: dayLabels,
    datasets: [
      {
        label: 'Cumulative Cost (PLN)',
        data: cumulativeCosts,
        borderColor: 'rgb(128, 0, 128)',
        backgroundColor: 'rgba(128, 0, 128, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.1,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
    },
  };

  const demandInventoryOptions = {
    responsive: true,
    maintainAspectRatio: true,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Demand vs. Inventory',
      },
    },
    scales: {
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        title: {
          display: true,
          text: 'Demand (kg)',
        },
      },
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        title: {
          display: true,
          text: 'Inventory (kg)',
        },
        grid: {
          drawOnChartArea: false,
        },
      },
    },
  };

  const orderOptions = {
    ...chartOptions,
    plugins: {
      ...chartOptions.plugins,
      title: {
        display: true,
        text: 'Order Amounts',
      },
    },
    scales: {
      y: {
        title: {
          display: true,
          text: 'Order Amount (kg)',
        },
      },
    },
  };

  const costsOptions = {
    ...chartOptions,
    plugins: {
      ...chartOptions.plugins,
      title: {
        display: true,
        text: 'Daily Costs',
      },
    },
    scales: {
      x: {
        stacked: true,
      },
      y: {
        stacked: true,
        title: {
          display: true,
          text: 'Cost (PLN)',
        },
      },
    },
  };

  const cumulativeOptions = {
    ...chartOptions,
    plugins: {
      ...chartOptions.plugins,
      title: {
        display: true,
        text: 'Cumulative Cost',
      },
    },
    scales: {
      y: {
        title: {
          display: true,
          text: 'Cumulative Cost (PLN)',
        },
      },
    },
  };

  return (
    <Box className="prediction-result">
      <Typography variant="h5" component="h2" gutterBottom>
        {messages.predictionResult.title}
      </Typography>
      
      <TableContainer component={Paper} className="prediction-table">
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>
                <Typography variant="subtitle2" fontWeight="bold">
                  {messages.predictionResult.headers.day}
                </Typography>
              </TableCell>
              <TableCell align="right">
                <Typography variant="subtitle2" fontWeight="bold">
                  {messages.predictionResult.headers.orderAmount}
                </Typography>
              </TableCell>
              <TableCell align="right">
                <Typography variant="subtitle2" fontWeight="bold">
                  {messages.predictionResult.headers.consumedAmount}
                </Typography>
              </TableCell>
              <TableCell align="right">
                <Typography variant="subtitle2" fontWeight="bold">
                  {messages.predictionResult.headers.remainingAmount}
                </Typography>
              </TableCell>
              <TableCell>
                <Typography variant="subtitle2" fontWeight="bold">
                  {messages.predictionResult.headers.unit}
                </Typography>
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data.map((row, index) => (
              <TableRow key={index} className="prediction-row">
                <TableCell component="th" scope="row">
                  <Typography variant="body1">
                    {row.day}
                  </Typography>
                </TableCell>
                <TableCell align="right">
                  <Typography variant="body1" fontWeight="medium">
                    {(row.orderAmount ?? 0).toFixed(2)}
                  </Typography>
                </TableCell>
                <TableCell align="right">
                  <Typography variant="body1" fontWeight="medium">
                    {(row.consumedAmount ?? 0).toFixed(2)}
                  </Typography>
                </TableCell>
                <TableCell align="right">
                  <Typography variant="body1" fontWeight="medium">
                    {(row.remainingAmount ?? 0).toFixed(2)}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="body2" color="text.secondary">
                    {row.unit}
                  </Typography>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Charts Section */}
      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" component="h3" gutterBottom>
          Visualization
        </Typography>
        <Grid container spacing={3}>
          <Grid size={{ xs: 12, md: 6 }}>
            <Paper sx={{ p: 2 }}>
              <Chart type='bar' data={demandInventoryData} options={demandInventoryOptions} />
            </Paper>
          </Grid>
          <Grid size={{ xs: 12, md: 6 }}>
            <Paper sx={{ p: 2 }}>
              <Bar data={orderData} options={orderOptions} />
            </Paper>
          </Grid>
          {dailyPurchaseCosts.length > 0 && (
            <>
              <Grid size={{ xs: 12, md: 6 }}>
                <Paper sx={{ p: 2 }}>
                  <Bar data={costsData} options={costsOptions} />
                </Paper>
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <Paper sx={{ p: 2 }}>
                  <Line data={cumulativeData} options={cumulativeOptions} />
                </Paper>
              </Grid>
            </>
          )}
        </Grid>
      </Box>
    </Box>
  );
};

export default PredictionResult;
